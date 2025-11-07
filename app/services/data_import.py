# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : data_import.py
Desc :   Excel数据导入服务
"""

import openpyxl
from loguru import logger

from app.models.medical import Disease


class DataImportService:
    """数据导入服务"""

    @staticmethod
    async def import_from_excel(file_path: str) -> dict:
        """
        从Excel文件导入疾病和症状数据
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            导入统计信息
        """
        logger.info(f"开始从Excel文件导入数据: {file_path}")
        
        # 加载Excel文件
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        
        disease_count = 0
        
        # 跳过表头
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        
        for row in rows:
            if not row[0]:  # 跳过空行
                continue
            
            # 处理数据，row[0]=id, row[1]=title, row[2]=description
            disease_name = str(row[1]).strip() if row[1] is not None else None
            disease_desc = str(row[2]).strip() if row[2] is not None else None
            
            if not disease_name:
                continue
            
            # 创建或获取疾病
            disease, created = await Disease.get_or_create(
                name=disease_name,
                defaults={"description": disease_desc or f"{disease_name}相关症状"}
            )
            if created:
                disease_count += 1
                logger.info(f"创建疾病: {disease_name}")
            
            # 从疾病描述中提取症状关键词（这里简化处理，实际可能需要更复杂的逻辑）
            # 由于Excel中没有单独的症状列，我们基于描述生成一些通用症状
            # 或者等待后续手动配置
            logger.debug(f"疾病 {disease_name} 的描述已导入")
        
        result = {
            "diseases": disease_count
        }
        
        logger.info(f"数据导入完成: {result}")
        return result


__all__ = ["DataImportService"]
