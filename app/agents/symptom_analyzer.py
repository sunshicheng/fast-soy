# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : symptom_analyzer.py
Desc :   症状分析Agent实现
"""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from loguru import logger

from app.models.system import Agent
from app.models.medical import Disease


class SymptomAnalyzerAgent:
    """症状分析Agent"""
    
    def __init__(self, agent: Agent):
        """
        初始化症状分析Agent
        
        Args:
            agent: Agent配置对象
        """
        self.agent = agent
        self.config = agent.langchain_config or {}
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.config.get("model", "gpt-4"),
            temperature=self.config.get("temperature", 0.5),
            max_tokens=self.config.get("max_tokens", 1500)
        )
        
        # 初始化Prompt
        self.prompt = ChatPromptTemplate.from_template(
            agent.prompt_template or self._default_prompt()
        )
        
        # 输出解析器
        self.parser = JsonOutputParser()
    
    def _default_prompt(self) -> str:
        """默认提示词模板"""
        return """你是一个医学症状分析专家。

给定疾病信息：
疾病名称：{disease_name}
症状列表：{symptoms}

请分析并生成一个真实的患者画像。

输出格式为JSON。"""
    
    async def analyze(self, disease_id: int) -> Dict[str, Any]:
        """
        分析疾病症状，生成患者画像
        
        Args:
            disease_id: 疾病ID
            
        Returns:
            患者画像数据
        """
        logger.info(f"开始分析疾病症状，疾病ID: {disease_id}")
        
        # 获取疾病和症状信息
        disease = await Disease.get(id=disease_id).prefetch_related(
            'disease_symptoms__symptom'
        )
        
        symptoms = [
            ds.symptom.name 
            for ds in disease.disease_symptoms
        ]
        
        logger.info(f"疾病: {disease.name}, 症状数量: {len(symptoms)}")
        
        # 构建LangChain链
        chain = self.prompt | self.llm | self.parser
        
        # 执行分析
        try:
            result = await chain.ainvoke({
                "disease_name": disease.name,
                "symptoms": ", ".join(symptoms)
            })
            
            logger.info(f"症状分析完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"症状分析失败: {e}")
            # 返回默认画像
            return {
                "age": 45,
                "gender": "未知",
                "main_symptoms": symptoms[:3] if len(symptoms) >= 3 else symptoms,
                "symptom_duration": "1周",
                "severity": "中等",
                "additional_info": f"患有{disease.name}"
            }


__all__ = ["SymptomAnalyzerAgent"]
