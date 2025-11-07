# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : init_medical_data.py
Desc :   初始化医疗数据脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise
from loguru import logger

from app.settings import APP_SETTINGS
from app.services.data_import import DataImportService


async def init_data():
    """初始化医疗数据"""
    # 初始化数据库连接
    await Tortoise.init(config=APP_SETTINGS.TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    logger.info("数据库初始化完成")
    
    # 导入Excel数据
    excel_file = Path(__file__).resolve().parent.parent / "document/mvp/CMB-Clin-summary.xlsx"
    
    if not excel_file.exists():
        logger.error(f"Excel文件不存在: {excel_file}")
        return
    
    result = await DataImportService.import_from_excel(str(excel_file))
    
    logger.info(f"导入完成: 疾病 {result['diseases']} 个, 症状 {result['symptoms']} 个, 关联 {result['relations']} 个")
    
    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_data())
