# -*- coding: utf-8 -*-
"""
Author : Mr.Sun
Datetime :  2025/11/6
FileName : init_agents.py
Desc :   初始化Agent配置脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise
from loguru import logger

from app.settings import APP_SETTINGS
from app.models.system import Agent, AgentType, StatusType


async def init_agents():
    """初始化Agent配置"""
    # 初始化数据库连接
    await Tortoise.init(config=APP_SETTINGS.TORTOISE_ORM)
    
    logger.info("开始初始化Agent配置")
    
    # Agent配置数据
    agents_config = [
        {
            "name": "主控Agent",
            "agent_type": AgentType.BUSINESS,
            "description": "负责协调整个测试流程，调度其他子Agent完成任务",
            "status_type": StatusType.enable,
            "version": "1.0.0",
            "langchain_config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "prompt_template": """你是一个测试流程协调员，负责管理医疗诊断测试的整个流程。

你的职责是：
1. 接收测试任务（疾病ID）
2. 调用症状分析Agent分析疾病症状
3. 调用患者对话Agent模拟患者与医生对话
4. 调用结果判断Agent分析诊断结果
5. 记录整个流程的执行状态

请按照流程顺序执行，确保每个步骤都正确完成。""",
            "tools": ["symptom_analyzer", "patient_dialog", "result_analyzer"]
        },
        {
            "name": "症状分析Agent",
            "agent_type": AgentType.FUNCTION,
            "description": "分析疾病的症状特征，生成患者画像",
            "status_type": StatusType.enable,
            "version": "1.0.0",
            "langchain_config": {
                "model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 1500
            },
            "prompt_template": """你是一个医学症状分析专家。

给定疾病信息：
疾病名称：{disease_name}
症状列表：{symptoms}

请分析并生成一个真实的患者画像，包括：
1. 年龄和性别
2. 主要症状的严重程度
3. 症状的持续时间
4. 其他相关信息

输出格式为JSON：
{{
    "age": 年龄,
    "gender": "性别",
    "main_symptoms": ["主要症状1", "主要症状2"],
    "symptom_duration": "持续时间",
    "severity": "严重程度",
    "additional_info": "其他信息"
}}""",
            "tools": []
        },
        {
            "name": "患者对话Agent",
            "agent_type": AgentType.FUNCTION,
            "description": "模拟患者，根据症状画像与医生API进行对话",
            "status_type": StatusType.enable,
            "version": "1.0.0",
            "langchain_config": {
                "model": "gpt-4",
                "temperature": 0.8,
                "max_tokens": 1000
            },
            "prompt_template": """你是一个患者，正在向医生描述你的症状。

你的基本信息：
{patient_profile}

医生的问题：{doctor_question}

请根据你的症状画像，用自然、真实的语言回答医生的问题。
- 如实描述症状
- 不要使用过于专业的医学术语
- 回答要简洁明确
- 如果医生问到你不确定的信息，可以说"不太清楚"或"记不清了"

直接输出你的回答，不要包含其他解释。""",
            "tools": []
        },
        {
            "name": "结果判断Agent",
            "agent_type": AgentType.FUNCTION,
            "description": "提取医生的诊断结果，并与预期疾病进行比对",
            "status_type": StatusType.enable,
            "version": "1.0.0",
            "langchain_config": {
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "prompt_template": """你是一个医学诊断结果分析专家。

医生的最终回复：
{doctor_response}

预期疾病：{expected_disease}

请执行以下任务：
1. 从医生的回复中提取诊断结果
2. 判断诊断是否与预期疾病一致
3. 给出匹配度评分（0-100）

输出格式为JSON：
{{
    "diagnosed_disease": "医生诊断的疾病",
    "is_match": true/false,
    "match_score": 匹配度评分,
    "analysis": "分析说明"
}}""",
            "tools": []
        }
    ]
    
    # 创建或更新Agent
    created_count = 0
    updated_count = 0
    
    for agent_data in agents_config:
        agent, created = await Agent.get_or_create(
            name=agent_data["name"],
            defaults=agent_data
        )
        
        if created:
            created_count += 1
            logger.info(f"创建Agent: {agent.name}")
        else:
            # 更新已存在的Agent
            for key, value in agent_data.items():
                if key != "name":
                    setattr(agent, key, value)
            await agent.save()
            updated_count += 1
            logger.info(f"更新Agent: {agent.name}")
    
    logger.info(f"Agent配置完成: 创建 {created_count} 个, 更新 {updated_count} 个")
    
    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_agents())
