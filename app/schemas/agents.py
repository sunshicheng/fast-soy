# -*- coding: utf-8 -*-
"""
Agent Schema定义
"""

from typing import Annotated

from pydantic import BaseModel, Field

from app.models.system import AgentType, StatusType


class AgentBase(BaseModel):
    """Agent基础Schema"""
    name: Annotated[str | None, Field(alias="name", max_length=255, title="Agent名称")] = None
    agent_type: Annotated[AgentType | None, Field(alias="agentType", title="Agent类型")] = None
    description: Annotated[str | None, Field(alias="description", title="Agent描述")] = None
    status_type: Annotated[StatusType | None, Field(alias="statusType", title="状态")] = None
    version: Annotated[str | None, Field(alias="version", max_length=50, title="版本号")] = None
    config: Annotated[dict | None, Field(alias="config", title="Agent配置")] = None

    class Config:
        populate_by_name = True


class AgentSearch(AgentBase):
    """Agent搜索Schema"""
    current: Annotated[int | None, Field(description="页码", ge=1)] = 1
    size: Annotated[int | None, Field(description="每页数量", ge=1, le=100)] = 10


class AgentCreate(AgentBase):
    """Agent创建Schema"""
    name: Annotated[str, Field(alias="name", max_length=255, title="Agent名称")]
    agent_type: Annotated[AgentType, Field(alias="agentType", title="Agent类型")]


class AgentUpdate(AgentBase):
    """Agent更新Schema"""
    ...


__all__ = ["AgentBase", "AgentSearch", "AgentCreate", "AgentUpdate"]

