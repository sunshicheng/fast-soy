# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : master_agent.py
Desc :   主控Agent实现
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from app.models.system import Agent
from app.models.medical import (
    Disease, TestExecution, ExecutionStep, Conversation,
    ExecutionStatus, StepStatus
)
from app.services import DoctorService
from .symptom_analyzer import SymptomAnalyzerAgent
from .patient_dialog import PatientDialogAgent
from .result_analyzer import ResultAnalyzerAgent


class MasterAgent:
    """主控Agent - 协调整个测试流程"""
    
    def __init__(self):
        """初始化主控Agent"""
        self.symptom_agent = None
        self.patient_agent = None
        self.result_agent = None
    
    async def initialize(self):
        """初始化所有子Agent"""
        # 加载Agent配置
        symptom_agent_config = await Agent.get(name="症状分析Agent")
        patient_agent_config = await Agent.get(name="患者对话Agent")
        result_agent_config = await Agent.get(name="结果判断Agent")
        
        # 初始化子Agent
        self.symptom_agent = SymptomAnalyzerAgent(symptom_agent_config)
        self.patient_agent = PatientDialogAgent(patient_agent_config)
        self.result_agent = ResultAnalyzerAgent(result_agent_config)
        
        logger.info("主控Agent初始化完成")
    
    async def run_test(self, disease_id: int, max_rounds: int = 10) -> str:
        """
        运行完整的测试流程
        
        Args:
            disease_id: 疾病ID
            max_rounds: 最大对话轮次
            
        Returns:
            执行ID
        """
        # 创建测试执行记录
        execution_id = f"test_{uuid.uuid4().hex[:12]}"
        disease = await Disease.get(id=disease_id)
        
        execution = await TestExecution.create(
            execution_id=execution_id,
            disease=disease,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        logger.info(f"开始测试执行: {execution_id}, 疾病: {disease.name}")
        
        try:
            # Step 1: 症状分析
            patient_profile = await self._execute_step(
                execution,
                "symptom_analysis",
                self._run_symptom_analysis,
                disease_id
            )
            
            # Step 2: 患者对话
            await self._execute_step(
                execution,
                "patient_dialog",
                self._run_patient_dialog,
                execution,
                disease,
                patient_profile,
                max_rounds
            )
            
            # Step 3: 结果判断
            last_conversation = await Conversation.filter(
                execution=execution,
                role="doctor"
            ).order_by('-round').first()
            
            if last_conversation:
                await self._execute_step(
                    execution,
                    "result_analysis",
                    self._run_result_analysis,
                    last_conversation.message,
                    disease.name
                )
            
            # 更新执行状态为成功
            execution.status = ExecutionStatus.SUCCESS
            execution.end_time = datetime.now()
            await execution.save()
            
            logger.info(f"测试执行完成: {execution_id}")
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            execution.status = ExecutionStatus.ERROR
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            await execution.save()
            raise
        
        return execution_id
    
    async def _execute_step(
        self,
        execution: TestExecution,
        step_name: str,
        func,
        *args
    ) -> Any:
        """
        执行单个步骤并记录
        
        Args:
            execution: 执行记录
            step_name: 步骤名称
            func: 执行函数
            *args: 函数参数
            
        Returns:
            步骤输出结果
        """
        # 获取当前步骤序号
        step_count = await ExecutionStep.filter(execution=execution).count()
        
        # 创建步骤记录
        step = await ExecutionStep.create(
            execution=execution,
            step_name=step_name,
            step_order=step_count + 1,
            status=StepStatus.RUNNING,
            start_time=datetime.now()
        )
        
        logger.info(f"开始执行步骤: {step_name}")
        
        try:
            # 执行步骤
            result = await func(*args)
            
            # 更新步骤状态
            step.status = StepStatus.SUCCESS
            step.output_data = result if isinstance(result, dict) else {"result": str(result)}
            step.end_time = datetime.now()
            await step.save()
            
            logger.info(f"步骤 {step_name} 执行成功")
            return result
            
        except Exception as e:
            logger.error(f"步骤 {step_name} 执行失败: {e}")
            step.status = StepStatus.ERROR
            step.error_message = str(e)
            step.end_time = datetime.now()
            await step.save()
            raise
    
    async def _run_symptom_analysis(self, disease_id: int) -> Dict[str, Any]:
        """运行症状分析"""
        return await self.symptom_agent.analyze(disease_id)
    
    async def _run_patient_dialog(
        self,
        execution: TestExecution,
        disease: Disease,
        patient_profile: Dict[str, Any],
        max_rounds: int
    ) -> Dict[str, Any]:
        """运行患者对话"""
        session_id = f"session_{execution.execution_id}"
        
        # 初始消息
        initial_message = f"医生您好，我感觉身体不太舒服，想咨询一下。"
        
        for round_num in range(1, max_rounds + 1):
            logger.info(f"对话轮次 {round_num}/{max_rounds}")
            
            # 患者消息
            if round_num == 1:
                patient_message = initial_message
            else:
                # 获取上一轮医生的问题
                last_doctor_msg = await Conversation.filter(
                    execution=execution,
                    role="doctor"
                ).order_by('-round').first()
                
                if not last_doctor_msg:
                    break
                
                # 患者根据画像回答
                patient_message = await self.patient_agent.respond(
                    patient_profile,
                    last_doctor_msg.message
                )
            
            # 记录患者消息
            await Conversation.create(
                execution=execution,
                round=round_num,
                role="patient",
                message=patient_message
            )
            
            # 调用医生API获取回复
            doctor_response = await DoctorService.chat(
                session_id=session_id,
                message=patient_message,
                patient_info=patient_profile if round_num == 1 else None
            )
            
            # 记录医生消息
            await Conversation.create(
                execution=execution,
                round=round_num,
                role="doctor",
                message=doctor_response
            )
            
            # 检查是否包含诊断结果（简单判断）
            if any(keyword in doctor_response for keyword in ["诊断", "考虑", "可能是", "建议"]):
                logger.info(f"检测到诊断结果，结束对话")
                break
        
        return {"total_rounds": round_num, "status": "completed"}
    
    async def _run_result_analysis(
        self,
        doctor_response: str,
        expected_disease: str
    ) -> Dict[str, Any]:
        """运行结果分析"""
        return await self.result_agent.analyze(doctor_response, expected_disease)


__all__ = ["MasterAgent"]
