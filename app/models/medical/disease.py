# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : disease.py
Desc :   疾病和症状模型定义
"""

from tortoise import fields

from app.models.system.utils import BaseModel, TimestampMixin


class Disease(BaseModel, TimestampMixin):
    """疾病模型"""
    id = fields.IntField(pk=True, description="疾病ID")
    name = fields.CharField(max_length=200, unique=True, description="疾病名称")
    description = fields.TextField(null=True, description="疾病描述")
    department = fields.CharField(max_length=100, null=True, description="所属科室")

    class Meta:
        table = "diseases"
        table_description = "疾病表"
        indexes = [
            ("name",),
        ]


__all__ = ["Disease"]
