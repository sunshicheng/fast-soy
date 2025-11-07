# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : test_execution.py
Desc :   测试执行相关模型定义
"""

from tortoise import fields

from app.models.system.utils import BaseModel, TimestampMixin, StrEnum


class ExecutionStatus(StrEnum):
    """测试执行状态枚举"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"    # 失败
    ERROR = "error"      # 错误


class StepStatus(StrEnum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class TestExecution(BaseModel, TimestampMixin):
    """测试执行记录模型"""
    id = fields.IntField(pk=True, description="执行ID")
    execution_id = fields.CharField(max_length=100, unique=True, description="执行唯一标识")
    disease = fields.ForeignKeyField("app_system.Disease", related_name="test_executions", description="测试疾病")
    status = fields.CharEnumField(enum_type=ExecutionStatus, default=ExecutionStatus.PENDING, description="执行状态")
    start_time = fields.DatetimeField(null=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")
    result = fields.JSONField(null=True, description="执行结果")
    error_message = fields.TextField(null=True, description="错误信息")

    class Meta:
        table = "test_executions"
        table_description = "测试执行记录表"
        indexes = [
            ("execution_id",),
            ("disease_id",),
            ("status",),
        ]


class ExecutionStep(BaseModel, TimestampMixin):
    """执行步骤模型"""
    id = fields.IntField(pk=True, description="步骤ID")
    execution = fields.ForeignKeyField("app_system.TestExecution", related_name="steps", description="所属执行")
    agent = fields.ForeignKeyField("app_system.Agent", related_name="execution_steps", null=True, description="执行Agent")
    step_name = fields.CharField(max_length=100, description="步骤名称")
    step_order = fields.IntField(description="步骤序号")
    status = fields.CharEnumField(enum_type=StepStatus, default=StepStatus.PENDING, description="步骤状态")
    start_time = fields.DatetimeField(null=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")
    input_data = fields.JSONField(null=True, description="输入数据")
    output_data = fields.JSONField(null=True, description="输出数据")
    error_message = fields.TextField(null=True, description="错误信息")

    class Meta:
        table = "execution_steps"
        table_description = "执行步骤表"
        indexes = [
            ("execution_id",),
            ("step_order",),
        ]


class Conversation(BaseModel, TimestampMixin):
    """对话记录模型"""
    id = fields.IntField(pk=True, description="对话ID")
    execution = fields.ForeignKeyField("app_system.TestExecution", related_name="conversations", description="所属执行")
    round = fields.IntField(description="对话轮次")
    role = fields.CharField(max_length=20, description="角色(doctor/patient)")
    message = fields.TextField(description="消息内容")
    timestamp = fields.DatetimeField(auto_now_add=True, description="时间戳")

    class Meta:
        table = "conversations"
        table_description = "对话记录表"
        indexes = [
            ("execution_id",),
            ("round",),
        ]


__all__ = ["ExecutionStatus", "StepStatus", "TestExecution", "ExecutionStep", "Conversation"]
