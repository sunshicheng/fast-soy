# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : patient_dialog.py
Desc :   患者对话Agent实现
"""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from app.models.system import Agent


class PatientDialogAgent:
    """患者对话Agent"""
    
    def __init__(self, agent: Agent):
        """
        初始化患者对话Agent
        
        Args:
            agent: Agent配置对象
        """
        self.agent = agent
        self.config = agent.langchain_config or {}
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.config.get("model", "gpt-4"),
            temperature=self.config.get("temperature", 0.8)
        )
        
        # 初始化Prompt
        self.prompt = ChatPromptTemplate.from_template(
            agent.prompt_template or self._default_prompt()
        )
    
    def _default_prompt(self) -> str:
        """默认提示词模板"""
        return """你是一个患者，正在向医生描述你的症状。

你的基本信息：
{patient_profile}

医生的问题：{doctor_question}

请根据你的症状画像，用自然、真实的语言回答医生的问题。"""
    
    async def respond(
        self, 
        patient_profile: Dict[str, Any], 
        doctor_question: str
    ) -> str:
        """
        作为患者回复医生的问题
        
        Args:
            patient_profile: 患者画像
            doctor_question: 医生的问题
            
        Returns:
            患者的回答
        """
        logger.info(f"患者Agent收到医生问题: {doctor_question}")
        
        # 构建LangChain链
        chain = self.prompt | self.llm
        
        try:
            result = await chain.ainvoke({
                "patient_profile": json.dumps(patient_profile, ensure_ascii=False, indent=2),
                "doctor_question": doctor_question
            })
            
            response = result.content if hasattr(result, 'content') else str(result)
            logger.info(f"患者回答: {response}")
            return response
            
        except Exception as e:
            logger.error(f"患者对话生成失败: {e}")
            return "我感觉不太舒服，有一些症状需要您帮忙看看。"


__all__ = ["PatientDialogAgent"]
