# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : api_token.py
Desc :   医生API Token管理模型
"""

from tortoise import fields

from app.models.system.utils import BaseModel, TimestampMixin


class DoctorApiToken(BaseModel, TimestampMixin):
    """医生API Token模型"""
    id = fields.IntField(pk=True, description="Token ID")
    token = fields.TextField(description="访问令牌")
    expires_at = fields.DatetimeField(description="过期时间")
    is_active = fields.BooleanField(default=True, description="是否有效")

    class Meta:
        table = "doctor_api_tokens"
        table_description = "医生API Token表"
        indexes = [
            ("is_active",),
            ("expires_at",),
        ]


__all__ = ["DoctorApiToken"]
