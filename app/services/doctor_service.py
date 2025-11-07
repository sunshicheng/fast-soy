# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : doctor_service.py
Desc :   医生API调用服务
"""

from typing import AsyncIterator
import httpx
from loguru import logger

from .token_manager import TokenManager


class DoctorService:
    """医生API服务"""
    
    BASE_URL = "https://open.cn2030.com"
    
    @classmethod
    async def chat_stream(
        cls, 
        session_id: str, 
        message: str,
        patient_info: dict = None
    ) -> AsyncIterator[str]:
        """
        与医生API进行流式对话
        
        Args:
            session_id: 会话ID
            message: 患者消息
            patient_info: 患者信息（可选）
            
        Yields:
            医生的回复内容（流式）
        """
        # 获取有效Token
        token = await TokenManager.get_valid_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "sessionId": session_id,
            "query": message,
            "stream": True
        }
        
        # 如果有患者信息，添加到payload中
        if patient_info:
            payload["patientInfo"] = patient_info
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{cls.BASE_URL}/api/doctor/chat",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    
                    # 处理SSE流式响应
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # 去掉 "data: " 前缀
                            if data and data != "[DONE]":
                                yield data
                                
            except httpx.HTTPError as e:
                logger.error(f"医生API调用失败: {e}")
                raise
            except Exception as e:
                logger.error(f"医生API处理异常: {e}")
                raise
    
    @classmethod
    async def chat(
        cls,
        session_id: str,
        message: str,
        patient_info: dict = None
    ) -> str:
        """
        与医生API进行对话（非流式，等待完整响应）
        
        Args:
            session_id: 会话ID
            message: 患者消息
            patient_info: 患者信息（可选）
            
        Returns:
            医生的完整回复
        """
        full_response = ""
        async for chunk in cls.chat_stream(session_id, message, patient_info):
            full_response += chunk
        
        return full_response


__all__ = ["DoctorService"]
