# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6 13:56
FileName : agent.py
Desc :   Agent模型定义
"""

from enum import Enum

from tortoise import fields

from .utils import BaseModel, TimestampMixin, StatusType, StrEnum


class AgentType(StrEnum):
    """Agent类型枚举"""
    BUSINESS = "business"  # 业务场景类Agent
    FUNCTION = "function"  # 功能类Agent


class Agent(BaseModel, TimestampMixin):
    """Agent模型"""
    id = fields.IntField(pk=True, description="Agent ID")
    name = fields.CharField(max_length=255, unique=True, description="Agent名称")
    agent_type = fields.CharEnumField(enum_type=AgentType, description="Agent类型")
    description = fields.TextField(null=True, description="Agent描述")
    status_type = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable, description="状态")
    version = fields.CharField(max_length=50, default="1.0.0", description="版本号")
    config = fields.JSONField(null=True, description="Agent配置（JSON格式）")

    class Meta:
        table = "agents"
        table_description = "Agent表"
        indexes = [
            ("name",),
            ("agent_type",),
            ("status_type",),
        ]


__all__ = ["Agent", "AgentType"]
