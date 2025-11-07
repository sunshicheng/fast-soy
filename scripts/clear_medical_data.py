# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/7
FileName : clear_medical_data.py
Desc :   清理医疗数据
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise
from loguru import logger

from app.settings import APP_SETTINGS
from app.models.medical import Disease


async def clear_data():
    """清理医疗数据"""
    await Tortoise.init(config=APP_SETTINGS.TORTOISE_ORM)
    
    logger.info("开始清理医疗数据")
    
    # 删除疾病
    deleted_diseases = await Disease.all().delete()
    logger.info(f"删除疾病: {deleted_diseases} 条")
    
    logger.info("数据清理完成")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(clear_data())
