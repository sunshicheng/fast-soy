# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : disease.py
Desc :   疾病诊断相关API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from loguru import logger

from app.models.medical import Disease, TestExecution, ExecutionStep, Conversation
from app.agents import MasterAgent
from app.schemas.base import Success


router = APIRouter(prefix="/diagnosis", tags=["疾病诊断"])


class UpdateDiseaseRequest(BaseModel):
    """更新疾病请求"""
    description: str


class StartTestRequest(BaseModel):
    """开始测试请求"""
    disease_id: int
    max_rounds: int = 10


class TestExecutionResponse(BaseModel):
    """测试执行响应"""
    execution_id: str
    disease_name: str
    status: str


class ExecutionDetailResponse(BaseModel):
    """执行详情响应"""
    execution_id: str
    disease_name: str
    status: str
    start_time: str
    end_time: str | None
    steps: List[Dict[str, Any]]
    conversations: List[Dict[str, Any]]
    result: Dict[str, Any] | None


@router.post("/start", response_model=TestExecutionResponse)
async def start_test(request: StartTestRequest):
    """
    开始测试
    
    Args:
        request: 测试请求参数
        
    Returns:
        测试执行信息
    """
    try:
        # 检查疾病是否存在
        disease = await Disease.get_or_none(id=request.disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail="疾病不存在")
        
        # 初始化主控Agent
        master = MasterAgent()
        await master.initialize()
        
        # 运行测试
        execution_id = await master.run_test(
            disease_id=request.disease_id,
            max_rounds=request.max_rounds
        )
        
        # 获取执行记录
        execution = await TestExecution.get(execution_id=execution_id)
        
        return TestExecutionResponse(
            execution_id=execution.execution_id,
            disease_name=disease.name,
            status=execution.status.value
        )
        
    except Exception as e:
        logger.error(f"测试启动失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{execution_id}", response_model=ExecutionDetailResponse)
async def get_execution_detail(execution_id: str):
    """
    获取测试执行详情
    
    Args:
        execution_id: 执行ID
        
    Returns:
        执行详情
    """
    try:
        # 获取执行记录
        execution = await TestExecution.get(execution_id=execution_id).prefetch_related(
            'disease', 'steps', 'conversations'
        )
        
        # 获取步骤列表
        steps = await ExecutionStep.filter(execution=execution).order_by('step_order')
        steps_data = [
            {
                "step_name": step.step_name,
                "step_order": step.step_order,
                "status": step.status.value,
                "start_time": step.start_time.strftime("%Y-%m-%d %H:%M:%S") if step.start_time else None,
                "end_time": step.end_time.strftime("%Y-%m-%d %H:%M:%S") if step.end_time else None,
                "output_data": step.output_data,
                "error_message": step.error_message
            }
            for step in steps
        ]
        
        # 获取对话列表
        conversations = await Conversation.filter(execution=execution).order_by('round', 'create_time')
        conversations_data = [
            {
                "round": conv.round,
                "role": conv.role,
                "message": conv.message,
                "timestamp": conv.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for conv in conversations
        ]
        
        return ExecutionDetailResponse(
            execution_id=execution.execution_id,
            disease_name=execution.disease.name,
            status=execution.status.value,
            start_time=execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else "",
            end_time=execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else None,
            steps=steps_data,
            conversations=conversations_data,
            result=execution.result
        )
        
    except Exception as e:
        logger.error(f"获取执行详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/diseases/{disease_id}")
async def update_disease(disease_id: int, request: UpdateDiseaseRequest):
    """
    更新疾病描述
    
    Args:
        disease_id: 疾病ID
        request: 更新请求
        
    Returns:
        更新结果
    """
    try:
        disease = await Disease.get_or_none(id=disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail="疾病不存在")
        
        disease.description = request.description
        await disease.save()
        
        return Success(msg="更新成功", data={"id": disease_id})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新疾病失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diseases")
async def get_diseases():
    """
    获取疾病列表
    
    Returns:
        疾病列表
    """
    try:
        diseases = await Disease.all()
        
        result = [
            {
                "id": disease.id,
                "name": disease.name,
                "description": disease.description,
                "symptoms_count": 0  # 不再使用症状表
            }
            for disease in diseases
        ]
        
        return Success(data=result)
        
    except Exception as e:
        logger.error(f"获取疾病列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
