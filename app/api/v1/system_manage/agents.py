# -*- coding: utf-8 -*-
"""
Agent管理API
"""

from fastapi import APIRouter
from tortoise.expressions import Q

from app.api.v1.utils import insert_log
from app.controllers.agent import agent_controller
from app.models.system import LogType, LogDetailType
from app.schemas.base import Success, SuccessExtra, CommonIds
from app.schemas.agents import AgentCreate, AgentUpdate, AgentSearch

router = APIRouter()


@router.post("/agents/all/", summary="查看Agent列表")
async def _(obj_in: AgentSearch):
    """获取Agent列表（支持搜索和分页）"""
    q = Q()
    if obj_in.name:
        q &= Q(name__contains=obj_in.name)
    if obj_in.agent_type:
        q &= Q(agent_type=obj_in.agent_type)
    if obj_in.status_type:
        q &= Q(status_type=obj_in.status_type)

    total, agent_objs = await agent_controller.list(
        page=obj_in.current,
        page_size=obj_in.size,
        search=q,
        order=["-id"]
    )
    
    records = [await agent_obj.to_dict() for agent_obj in agent_objs]
    data = {"records": records}
    
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentGetList,
        by_user_id=0
    )
    return SuccessExtra(data=data, total=total, current=obj_in.current, size=obj_in.size)


@router.get("/agents/{agent_id}", summary="查看Agent详情")
async def get_agent(agent_id: int):
    """获取Agent详情"""
    agent_obj = await agent_controller.get(id=agent_id)
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentGetOne,
        by_user_id=0
    )
    return Success(data=await agent_obj.to_dict())


@router.post("/agents", summary="创建Agent")
async def _(agent_in: AgentCreate):
    """创建Agent"""
    existing_agent = await agent_controller.get_by_name(agent_in.name)
    if existing_agent:
        return Success(code="4090", msg="Agent名称已存在")
    
    new_agent = await agent_controller.create(obj_in=agent_in)
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentCreateOne,
        by_user_id=0
    )
    return Success(msg="创建成功", data={"created_id": new_agent.id})


@router.patch("/agents/{agent_id}", summary="更新Agent")
async def _(agent_id: int, agent_in: AgentUpdate):
    """更新Agent"""
    agent = await agent_controller.get(id=agent_id)
    
    if agent_in.name and agent_in.name != agent.name:
        existing_agent = await agent_controller.get_by_name(agent_in.name)
        if existing_agent:
            return Success(code="4090", msg="Agent名称已存在")
    
    await agent_controller.update(id=agent_id, obj_in=agent_in)
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentUpdateOne,
        by_user_id=0
    )
    return Success(msg="更新成功", data={"updated_id": agent_id})


@router.delete("/agents/{agent_id}", summary="删除Agent")
async def _(agent_id: int):
    """删除Agent"""
    await agent_controller.remove(id=agent_id)
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentDeleteOne,
        by_user_id=0
    )
    return Success(msg="删除成功", data={"deleted_id": agent_id})


@router.delete("/agents", summary="批量删除Agent")
async def _(obj_in: CommonIds):
    """批量删除Agent"""
    deleted_ids = []
    for agent_id in obj_in.ids:
        agent_obj = await agent_controller.get(id=int(agent_id))
        await agent_obj.delete()
        deleted_ids.append(int(agent_id))
    
    await insert_log(
        log_type=LogType.AdminLog,
        log_detail_type=LogDetailType.AgentBatchDeleteOne,
        by_user_id=0
    )
    return Success(msg="批量删除成功", data={"deleted_ids": deleted_ids})

