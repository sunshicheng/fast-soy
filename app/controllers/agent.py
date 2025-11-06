# -*- coding: utf-8 -*-
"""
Agent业务逻辑控制器
"""

from app.core.crud import CRUDBase
from app.models.system import Agent, AgentType, StatusType
from app.schemas.agents import AgentCreate, AgentUpdate


class AgentController(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    """Agent业务逻辑控制器"""
    
    def __init__(self):
        super().__init__(model=Agent)
    
    async def get_by_name(self, name: str) -> Agent | None:
        """根据名称获取Agent"""
        return await self.model.filter(name=name).first()
    
    async def get_by_type(self, agent_type: AgentType) -> list[Agent]:
        """根据类型获取Agent列表"""
        return await self.model.filter(agent_type=agent_type, status_type=StatusType.enable).all()


# 创建控制器实例
agent_controller = AgentController()

