# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : token_manager.py
Desc :   医生API Token管理服务
"""

from datetime import datetime, timedelta
import httpx
from loguru import logger

from app.models.medical import DoctorApiToken


class TokenManager:
    """医生API Token管理器"""
    
    BASE_URL = "https://open.cn2030.com"
    
    @classmethod
    async def get_valid_token(cls) -> str:
        """
        获取有效的Token，如果不存在或已过期则自动刷新
        
        Returns:
            有效的访问令牌
        """
        # 查找有效且未过期的Token
        now = datetime.now()
        token_record = await DoctorApiToken.filter(
            is_active=True,
            expires_at__gt=now
        ).order_by('-create_time').first()
        
        if token_record:
            logger.info("使用已有的有效Token")
            return token_record.token
        
        # 需要获取新Token
        logger.info("获取新的Token")
        return await cls.fetch_new_token()
    
    @classmethod
    async def fetch_new_token(cls) -> str:
        """
        从医生API获取新的Token
        
        Returns:
            新获取的访问令牌
        """
        async with httpx.AsyncClient() as client:
            try:
                # 调用登录接口获取Token
                response = await client.post(
                    f"{cls.BASE_URL}/api/doctor/login",
                    json={
                        "username": "test_user",  # 需要配置实际的用户名
                        "password": "test_password"  # 需要配置实际的密码
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                token = data.get("data", {}).get("token")
                
                if not token:
                    raise ValueError("Token获取失败，响应中没有token字段")
                
                # 保存Token到数据库（假设有效期为2小时）
                expires_at = datetime.now() + timedelta(hours=2)
                
                # 将旧Token设置为无效
                await DoctorApiToken.filter(is_active=True).update(is_active=False)
                
                # 保存新Token
                await DoctorApiToken.create(
                    token=token,
                    expires_at=expires_at,
                    is_active=True
                )
                
                logger.info(f"成功获取新Token，过期时间: {expires_at}")
                return token
                
            except httpx.HTTPError as e:
                logger.error(f"获取Token失败: {e}")
                raise
            except Exception as e:
                logger.error(f"Token处理异常: {e}")
                raise


__all__ = ["TokenManager"]
