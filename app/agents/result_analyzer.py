# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : result_analyzer.py
Desc :   结果判断Agent实现
"""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from loguru import logger

from app.models.system import Agent


class ResultAnalyzerAgent:
    """结果判断Agent"""
    
    def __init__(self, agent: Agent):
        """
        初始化结果判断Agent
        
        Args:
            agent: Agent配置对象
        """
        self.agent = agent
        self.config = agent.langchain_config or {}
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.config.get("model", "gpt-4"),
            temperature=self.config.get("temperature", 0.3)
        )
        
        # 初始化Prompt
        self.prompt = ChatPromptTemplate.from_template(
            agent.prompt_template or self._default_prompt()
        )
        
        # 输出解析器
        self.parser = JsonOutputParser()
    
    def _default_prompt(self) -> str:
        """默认提示词模板"""
        return """你是一个医学诊断结果分析专家。

医生的最终回复：
{doctor_response}

预期疾病：{expected_disease}

请分析诊断结果并输出JSON格式。"""
    
    async def analyze(
        self, 
        doctor_response: str, 
        expected_disease: str
    ) -> Dict[str, Any]:
        """
        分析医生的诊断结果
        
        Args:
            doctor_response: 医生的回复
            expected_disease: 预期疾病名称
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析诊断结果，预期疾病: {expected_disease}")
        
        # 构建LangChain链
        chain = self.prompt | self.llm | self.parser
        
        try:
            result = await chain.ainvoke({
                "doctor_response": doctor_response,
                "expected_disease": expected_disease
            })
            
            logger.info(f"诊断结果分析完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"结果分析失败: {e}")
            # 返回默认结果
            return {
                "diagnosed_disease": "未能提取",
                "is_match": False,
                "match_score": 0,
                "analysis": f"分析失败: {str(e)}"
            }


__all__ = ["ResultAnalyzerAgent"]
