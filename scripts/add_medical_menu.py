# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : add_medical_menu.py
Desc :   添加医疗测试菜单到数据库
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise
from loguru import logger

from app.settings import APP_SETTINGS
from app.models.system import Menu, MenuType, StatusType, IconType


async def add_medical_menu():
    """添加医疗测试菜单"""
    # 初始化数据库连接
    await Tortoise.init(config=APP_SETTINGS.TORTOISE_ORM)
    
    logger.info("开始添加医疗测试菜单")
    
    try:
        # 1. 创建医疗测试父菜单（目录）
        medical_parent, created = await Menu.get_or_create(
            route_name="medical",
            defaults={
                "menu_name": "医疗测试",
                "menu_type": MenuType.catalog,
                "route_path": "/medical",
                "parent_id": 0,
                "order": 8,
                "i18n_key": "route.medical",
                "icon": "mdi:hospital-box",
                "icon_type": IconType.iconify,
                "status_type": StatusType.enable,
                "hide_in_menu": False
            }
        )
        
        if created:
            logger.info(f"创建医疗测试父菜单成功，ID: {medical_parent.id}")
        else:
            logger.info(f"医疗测试父菜单已存在，ID: {medical_parent.id}")
        
        # 2. 创建疾病列表子菜单
        disease_list_menu, created = await Menu.get_or_create(
            route_name="medical_disease-list",
            defaults={
                "menu_name": "疾病列表",
                "menu_type": MenuType.menu,
                "route_path": "/medical/disease-list",
                "component": "view.medical_disease-list",
                "parent_id": medical_parent.id,
                "order": 1,
                "i18n_key": "route.medical_disease-list",
                "icon": "mdi:virus",
                "icon_type": IconType.iconify,
                "status_type": StatusType.enable,
                "hide_in_menu": False
            }
        )
        
        if created:
            logger.info(f"创建疾病列表菜单成功，ID: {disease_list_menu.id}")
        else:
            logger.info(f"疾病列表菜单已存在，ID: {disease_list_menu.id}")
        
        # 3. 更新旧的测试执行菜单（如果存在）
        old_menu = await Menu.get_or_none(route_name="medical_execution")
        if old_menu:
            logger.info(f"删除旧的测试执行菜单，ID: {old_menu.id}")
            await old_menu.delete()
        
        # 4. 创建新的执行详情菜单（隐藏）
        execution_menu, created = await Menu.get_or_create(
            route_name="medical_execution-detail",
            defaults={
                "menu_name": "执行详情",
                "menu_type": MenuType.menu,
                "route_path": "/medical/execution-detail/:id",
                "path_param": ":id",
                "component": "view.medical_execution-detail",
                "parent_id": medical_parent.id,
                "order": 2,
                "i18n_key": "route.medical_execution-detail",
                "status_type": StatusType.enable,
                "hide_in_menu": True,  # 隐藏在菜单中
                "active_menu_id": disease_list_menu.id  # 激活疾病列表菜单
            }
        )
        
        if created:
            logger.info(f"创建执行详情菜单成功，ID: {execution_menu.id}")
        else:
            logger.info(f"执行详情菜单已存在，ID: {execution_menu.id}")
        
        logger.info("医疗测试菜单添加完成！")
        logger.info("请刷新前端页面查看新菜单")
        
    except Exception as e:
        logger.error(f"添加菜单失败: {e}")
        raise
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_medical_menu())
