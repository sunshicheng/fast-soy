# 医疗诊断测试平台 MVP 实现方案

## 📋 文档信息

- **文档版本**: v1.0
- **创建日期**: 2025-11-06
- **文档类型**: MVP实现方案
- **项目名称**: 医疗诊断测试平台（最小可行版本）

---

## 1. MVP 目标与范围

### 1.1 核心目标

通过主控 Agent 协调多个子 Agent，模拟患者与医生 API 交互，验证诊断准确性。

**核心流程**:
1. 从数据库随机选择一个疾病及其症状
2. **主控 Agent** 规划执行流程
3. **症状分析 Agent** 分析疾病症状，生成患者画像
4. **患者对话 Agent** 根据症状回答医生问题
5. **医生接口调用服务** 进行多轮对话
6. **结果判断 Agent** 提取诊断结果并与原始疾病对比
7. 记录完整的执行过程和测试结果

### 1.2 功能范围

**包含**:
- ✅ 疾病症状数据导入（CMB-Clin-summary.xlsx）
- ✅ Agent 配置和管理（基于现有 Agent 表）
- ✅ 主控 Agent（使用 LangChain 规划执行流程）
- ✅ 症状分析 Agent（分析疾病症状）
- ✅ 患者对话 Agent（模拟症状回答）
- ✅ 结果判断 Agent（诊断结果比对）
- ✅ Token 自动获取和管理
- ✅ 医生接口调用（非深度搜索模式）
- ✅ Agent 执行记录和对话历史
- ✅ 简单的 Web 界面展示

**不包含**:
- ❌ 深度搜索模式（MVP 只用非深度）
- ❌ 复杂的 LangGraph 状态图（使用简化的链式调用）
- ❌ Agent 动态注册和发现

---

## 2. 技术架构

### 2.1 技术选型

**后端**（使用现有技术栈）:
- Python 3.10+
- **FastAPI**（Web 框架）
- **Tortoise ORM**（数据库 ORM）
- **PostgreSQL / SQLite**（数据库）
- **LangChain**（Agent 框架）
- **httpx**（HTTP 客户端）

**前端**（使用现有技术栈）:
- Vue 3 + TypeScript
- Naive UI
- Pinia
- Vite

**AI 能力**:
- LangChain（Agent 编排）
- OpenAI API / 本地模型
- LangChain Tools（工具封装）

### 2.2 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                         前端界面                              │
│  - Agent 配置管理                                            │
│  - 测试启动页面                                               │
│  - 执行流程可视化                                             │
│  - 对话过程展示                                               │
│  - 结果对比展示                                               │
└─────────────────┬────────────────────────────────────────────┘
                  │ HTTP API
┌─────────────────┴────────────────────────────────────────────┐
│                      FastAPI 后端                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Agent 协作层（LangChain）               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │主控Agent │→ │症状分析  │→ │患者对话  │           │   │
│  │  │(Master)  │  │Agent     │  │Agent     │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │       ↓                              ↓               │   │
│  │  ┌──────────────────┐       ┌──────────────┐        │   │
│  │  │结果判断Agent     │       │医生接口服务  │        │   │
│  │  └──────────────────┘       └──────────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Agent控制器   │  │测试控制器    │  │Token管理器   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────┬────────────────────────────────────────────┘
                  │ Tortoise ORM
┌─────────────────┴────────────────────────────────────────────┐
│                   PostgreSQL / SQLite                         │
│  - agents (Agent配置表)           - agent_relations (关联表) │
│  - diseases (疾病表)              - symptoms (症状表)        │
│  - disease_symptoms (关联表)                                │
│  - test_executions (测试执行表)   - execution_steps (步骤表) │
│  - conversations (对话记录表)     - api_tokens (Token表)    │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 数据库设计（基于 Tortoise ORM）

### 3.1 现有表扩展

#### 3.1.1 Agent 表（已存在，需扩展）

**文件**: `app/models/system/agent.py`

```python
class Agent(BaseModel, TimestampMixin):
    """Agent模型（已存在，需添加字段）"""
    id = fields.IntField(pk=True, description="Agent ID")
    name = fields.CharField(max_length=255, unique=True, description="Agent名称")
    agent_type = fields.CharEnumField(enum_type=AgentType, description="Agent类型")
    description = fields.TextField(null=True, description="Agent描述")
    status_type = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable)
    version = fields.CharField(max_length=50, default="1.0.0")
    config = fields.JSONField(null=True, description="Agent配置")
    
    # 新增字段
    langchain_config = fields.JSONField(null=True, description="LangChain配置")
    prompt_template = fields.TextField(null=True, description="提示词模板")
    tools = fields.JSONField(null=True, description="工具列表")
```

#### 3.1.2 Agent 关联表（新增）

**文件**: `app/models/system/agent.py`

```python
class AgentRelation(BaseModel, TimestampMixin):
    """Agent关联关系表"""
    id = fields.IntField(pk=True)
    parent_agent = fields.ForeignKeyField(
        "models.Agent", 
        related_name="child_relations",
        description="父Agent"
    )
    child_agent = fields.ForeignKeyField(
        "models.Agent", 
        related_name="parent_relations",
        description="子Agent"
    )
    order = fields.IntField(default=0, description="执行顺序")
    condition = fields.JSONField(null=True, description="执行条件")
    
    class Meta:
        table = "agent_relations"
        unique_together = (("parent_agent", "child_agent"),)
```

### 3.2 新增医疗测试相关表

#### 3.2.1 疾病表

**文件**: `app/models/medical/disease.py`（新建）

```python
from tortoise import fields
from app.models.system.utils import BaseModel, TimestampMixin

class Disease(BaseModel, TimestampMixin):
    """疾病表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True, description="疾病名称")
    description = fields.TextField(null=True, description="疾病描述")
    
    class Meta:
        table = "diseases"
        table_description = "疾病表"


class Symptom(BaseModel, TimestampMixin):
    """症状表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, description="症状名称")
    description = fields.TextField(null=True, description="症状描述")
    
    class Meta:
        table = "symptoms"
        table_description = "症状表"


class DiseaseSymptom(BaseModel, TimestampMixin):
    """疾病症状关联表"""
    id = fields.IntField(pk=True)
    disease = fields.ForeignKeyField(
        "models.Disease",
        related_name="disease_symptoms",
        description="疾病"
    )
    symptom = fields.ForeignKeyField(
        "models.Symptom",
        related_name="symptom_diseases",
        description="症状"
    )
    severity = fields.CharField(max_length=50, null=True, description="严重程度")
    
    class Meta:
        table = "disease_symptoms"
        unique_together = (("disease", "symptom"),)
```

#### 3.2.2 测试执行表

**文件**: `app/models/medical/test_execution.py`（新建）

```python
from enum import Enum
from tortoise import fields
from app.models.system.utils import BaseModel, TimestampMixin, StrEnum

class ExecutionStatus(StrEnum):
    """执行状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class TestExecution(BaseModel, TimestampMixin):
    """测试执行表"""
    id = fields.IntField(pk=True)
    execution_id = fields.CharField(max_length=100, unique=True, description="执行ID")
    disease = fields.ForeignKeyField(
        "models.Disease",
        related_name="test_executions",
        description="目标疾病"
    )
    master_agent = fields.ForeignKeyField(
        "models.Agent",
        related_name="master_executions",
        description="主控Agent"
    )
    status = fields.CharEnumField(
        enum_type=ExecutionStatus,
        default=ExecutionStatus.PENDING,
        description="执行状态"
    )
    doctor_session_id = fields.CharField(max_length=100, null=True, description="医生接口SessionID")
    diagnosis_result = fields.TextField(null=True, description="诊断结果")
    is_correct = fields.BooleanField(null=True, description="是否诊断正确")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    error_message = fields.TextField(null=True, description="错误信息")
    
    class Meta:
        table = "test_executions"
        table_description = "测试执行表"


class ExecutionStep(BaseModel, TimestampMixin):
    """执行步骤表"""
    id = fields.IntField(pk=True)
    execution = fields.ForeignKeyField(
        "models.TestExecution",
        related_name="steps",
        description="所属执行"
    )
    agent = fields.ForeignKeyField(
        "models.Agent",
        related_name="execution_steps",
        description="执行的Agent"
    )
    step_order = fields.IntField(description="步骤顺序")
    step_name = fields.CharField(max_length=100, description="步骤名称")
    input_data = fields.JSONField(null=True, description="输入数据")
    output_data = fields.JSONField(null=True, description="输出数据")
    status = fields.CharEnumField(
        enum_type=ExecutionStatus,
        default=ExecutionStatus.PENDING
    )
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    error_message = fields.TextField(null=True)
    
    class Meta:
        table = "execution_steps"
        table_description = "执行步骤表"


class Conversation(BaseModel, TimestampMixin):
    """对话记录表"""
    id = fields.IntField(pk=True)
    execution = fields.ForeignKeyField(
        "models.TestExecution",
        related_name="conversations",
        description="所属执行"
    )
    round = fields.IntField(description="对话轮次")
    role = fields.CharField(max_length=20, description="角色：doctor/patient")
    message = fields.TextField(description="消息内容")
    raw_response = fields.TextField(null=True, description="原始响应JSON")
    
    class Meta:
        table = "conversations"
        table_description = "对话记录表"
```

#### 3.2.3 Token 表

**文件**: `app/models/medical/api_token.py`（新建）

```python
from tortoise import fields
from app.models.system.utils import BaseModel, TimestampMixin

class ApiToken(BaseModel, TimestampMixin):
    """API Token表"""
    id = fields.IntField(pk=True)
    access_token = fields.TextField(description="访问Token")
    refresh_token = fields.TextField(null=True, description="刷新Token")
    expires_in = fields.IntField(description="过期时间（秒）")
    expires_at = fields.DatetimeField(description="过期时间点")
    is_active = fields.BooleanField(default=True, description="是否有效")
    
    class Meta:
        table = "api_tokens"
        table_description = "API Token表"
```

---

## 4. Agent 协作流程设计

### 4.1 Agent 角色定义

#### 4.1.1 主控 Agent (Master Agent)

**类型**: `business`  
**责任**: 协调整个测试流程，调度子 Agent 执行

**配置示例**:
```json
{
  "name": "医疗测试主控Agent",
  "agent_type": "business",
  "config": {
    "max_rounds": 10,
    "timeout": 300
  },
  "langchain_config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.3
  },
  "prompt_template": "你是一个医疗测试协调员..."
}
```

**执行流程**:
1. 接收测试任务（疾病ID）
2. 调用症状分析 Agent 分析症状
3. 调用患者对话 Agent 与医生交互
4. 调用结果判断 Agent 分析结果
5. 汇总执行结果

---

#### 4.1.2 症状分析 Agent

**类型**: `function`  
**责任**: 分析疾病症状，生成患者画像

**输入**: 疾病ID  
**输出**: 症状列表、患者背景信息

**Prompt 示例**:
```
你是一个医学专家。给定疾病"{disease_name}"和症状列表：{symptoms}。

请分析：
1. 主要症状（按重要性排序）
2. 次要症状
3. 合理的患者画像（年龄、性别、病程）

返回JSON格式：
{{
  "primary_symptoms": [...],
  "secondary_symptoms": [...],
  "patient_profile": {{
    "age": 30,
    "gender": "男",
    "duration": "3天"
  }}
}}
```

---

#### 4.1.3 患者对话 Agent

**类型**: `function`  
**责任**: 模拟患者根据症状回答医生问题

**输入**: 医生问题、症状列表、患者画像  
**输出**: 患者回答

**Prompt 示例**:
```
你是一个患有{disease}的患者，症状包括：{symptoms}。

你的基本信息：
- 年龄：{age}
- 性别：{gender}
- 病程：{duration}

现在医生向你提问："{question}"

请根据你的症状如实回答：
- 如果医生问到的症状在你的症状列表中，明确回答"有"
- 如果不在列表中，回答"没有"或"不确定"
- 回答要自然、口语化，像真实患者一样
- 回答要简洁，不超过50字
```

---

#### 4.1.4 结果判断 Agent

**类型**: `function`  
**责任**: 提取医生诊断结果并与目标疾病对比

**输入**: 医生最后回复、目标疾病名称  
**输出**: 诊断结果、是否正确

**Prompt 示例**:
```
你是一个医学分析专家。从以下医生的回复中提取诊断结果：

"""
{doctor_response}
"""

目标疾病：{target_disease}

请分析：
1. 医生诊断的疾病名称（只返回疾病名，如果有多个，用逗号分隔）
2. 是否与目标疾病一致（包含也算正确）

返回JSON格式：
{{
  "diagnosis": "诊断疾病名称",
  "is_correct": true/false,
  "confidence": 0.95,
  "reason": "判断理由"
}}
```

---

### 4.2 Agent 协作流程

```
启动测试
    ↓
┌────────────────────────────────────┐
│         主控 Agent                     │
│  (协调整个流程、记录执行状态)         │
└────────────────┬─────────────────────┘
                 │
         Step 1: 调用症状分析 Agent
                 ↓
┌────────────────────────────────────┐
│      症状分析 Agent                  │
│  - 查询疾病和症状                      │
│  - 使用 LLM 分析症状重要性              │
│  - 生成患者画像                        │
└────────────────┬─────────────────────┘
                 │
         Step 2: 调用患者对话 Agent
                 │ (多轮对话，最多10轮)
                 ↓
┌────────────────────────────────────┐
│      患者对话 Agent                  │
│  ↓                                    │
│  1. 生成首次主诉（"医生您好，我..."） │
│  2. 调用医生接口                      │
│  3. 解析医生问题                      │
│  4. 使用 LLM 生成回答                  │
│  5. 调用医生接口                      │
│  6. 重复 3-5 直到得到诊断             │
└────────────────┬─────────────────────┘
                 │
         Step 3: 调用结果判断 Agent
                 ↓
┌────────────────────────────────────┐
│      结果判断 Agent                  │
│  - 使用 LLM 提取诊断结果              │
│  - 与目标疾病对比                      │
│  - 生成分析报告                        │
└────────────────┬─────────────────────┘
                 │
         返回主控 Agent
                 ↓
           记录执行结果
                 ↓
             完成
```

## 5. 核心功能实现

### 5.1 数据导入模块

**文件**: `app/services/data_import.py`

```python
import pandas as pd
from app.models.medical.disease import Disease, Symptom, DiseaseSymptom

async def import_disease_data(file_path: str):
    """导入疾病数据"""
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        # 创建疾病
        disease, created = await Disease.get_or_create(
            name=row['disease_name'],
            defaults={'description': row.get('description', '')}
        )
        
        # 解析症状（假设症状在 symptoms 列，逗号分隔）
        symptoms_str = row.get('symptoms', '')
        for symptom_name in symptoms_str.split(','):
            symptom_name = symptom_name.strip()
            if not symptom_name:
                continue
            
            symptom, _ = await Symptom.get_or_create(
                name=symptom_name
            )
            
            await DiseaseSymptom.get_or_create(
                disease=disease,
                symptom=symptom
            )
    
    print(f"导入完成：{len(df)} 条疾病数据")
```

---

### 5.2 Token 管理模块

**文件**: `app/services/token_manager.py`

```python
from datetime import datetime, timedelta
import httpx
from app.models.medical.api_token import ApiToken

class TokenManager:
    """医生 API Token 管理器"""
    
    BASE_URL = "https://centerapi.qschou.com"
    PHONE = "18226287291"
    SMS_CODE = "9527"
    AUTH_KEY = "qsevidence_pc"
    
    async def get_valid_token(self) -> str:
        """获取有效的 Token"""
        # 检查数据库中是否有未过期的 Token
        now = datetime.now()
        token = await ApiToken.filter(
            is_active=True,
            expires_at__gt=now
        ).order_by('-created_at').first()
        
        if token:
            return token.access_token
        
        # 没有有效 Token，重新获取
        return await self._fetch_new_token()
    
    async def _fetch_new_token(self) -> str:
        """获取新 Token"""
        async with httpx.AsyncClient(timeout=30) as client:
            # 第一步：发送短信验证码登录
            step1_data = {
                "country_code": "CN",
                "phone": self.PHONE,
                "sms_code": self.SMS_CODE,
                "auth_key": self.AUTH_KEY
            }
            
            resp1 = await client.post(
                f"{self.BASE_URL}/passport/sms/login",
                json=step1_data
            )
            resp1_data = resp1.json()
            
            # 获取 random_num
            user_list = resp1_data['data']['user_list']
            random_num = user_list[0]['random_num']
            
            # 第二步：获取 access_token
            step2_data = {"random_num": random_num}
            resp2 = await client.post(
                f"{self.BASE_URL}/passport/phone-multi-user",
                json=step2_data
            )
            resp2_data = resp2.json()
            
            access_token = resp2_data['data']['access_token']
            refresh_token = resp2_data['data']['refresh_token']
            expires_in = int(resp2_data['data']['expires_in'])
            
            # 使旧 Token 失效
            await ApiToken.filter(is_active=True).update(is_active=False)
            
            # 保存到数据库
            await ApiToken.create(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                expires_at=datetime.now() + timedelta(seconds=expires_in)
            )
            
            return access_token

# 全局实例
token_manager = TokenManager()
```

---

### 5.3 医生接口调用服务

**文件**: `app/services/doctor_service.py`

```python
import json
import httpx
from typing import Dict

class DoctorService:
    """医生接口服务"""
    
    API_URL = "https://test-chatgpt-api.qschou.com/qsevidence/session/stream"
    
    async def ask_doctor(
        self, 
        message: str, 
        session_id: str = "",
        token: str = None
    ) -> Dict:
        """向医生提问（非深度模式）"""
        headers = {
            "qsc-token": token,
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "ask",
            "session_id": session_id,
            "message": message,
            "is_deep_research": False
        }
        
        response_text = ""
        doctor_session_id = session_id
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", self.API_URL, json=data, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "{'timestamp'":
                            try:
                                event_data = json.loads(data_str)
                                
                                # 提取 session_id
                                if not doctor_session_id and 'session_id' in event_data:
                                    doctor_session_id = event_data['session_id']
                                
                                # 累积响应内容
                                if 'chunk' in event_data:
                                    response_text += event_data['chunk']
                            except:
                                pass
        
        return {
            "session_id": doctor_session_id,
            "message": response_text.strip(),
            "raw_response": response_text
        }

# 全局实例
doctor_service = DoctorService()
```

---

### 5.4 Agent 实现（基于 LangChain）

#### 5.4.1 症状分析 Agent

**文件**: `app/agents/symptom_analyzer.py`

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

from app.models.medical.disease import Disease

class PatientProfile(BaseModel):
    """患者画像"""
    primary_symptoms: List[str] = Field(description="主要症状")
    secondary_symptoms: List[str] = Field(description="次要症状")
    age: int = Field(description="年龄")
    gender: str = Field(description="性别")
    duration: str = Field(description="病程")


class SymptomAnalyzerAgent:
    """症状分析 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3
        )
        
        self.parser = PydanticOutputParser(pydantic_object=PatientProfile)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个医学专家。给定疾病和症状列表，请分析症状的重要性并生成合理的患者画像。

{format_instructions}"""),
            ("user", """疾病：{disease_name}
症状列表：{symptoms}

请分析：
1. 哪些是主要症状（最典型、最明显的）
2. 哪些是次要症状
3. 合理的患者画像（年龄、性别、病程）
""")
        ])
    
    async def analyze(self, disease_id: int) -> PatientProfile:
        """分析疾病症状"""
        # 查询疾病和症状
        disease = await Disease.get(id=disease_id).prefetch_related('disease_symptoms__symptom')
        symptoms = [ds.symptom.name for ds in disease.disease_symptoms]
        
        # 调用 LLM
        chain = self.prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "disease_name": disease.name,
            "symptoms": "、".join(symptoms),
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result
```

#### 5.4.2 患者对话 Agent

**文件**: `app/agents/patient_dialog.py`

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class PatientDialogAgent:
    """患者对话 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个患有{disease}的患者。

你的症状包括：
主要症状：{primary_symptoms}
次要症状：{secondary_symptoms}

你的基本信息：
- 年龄：{age}
- 性别：{gender}
- 病程：{duration}

回答原则：
1. 如果医生问到的症状在你的症状列表中，明确回答"有"
2. 如果不在列表中，回答"没有"或"不太确定"
3. 回答要自然、口语化，像真实患者一样
4. 回答要简洁，不超过50字
5. 对于年龄、性别等基本信息，根据你的画像回答
"""),
            ("user", "医生的问题：{question}")
        ])
    
    async def generate_first_message(self, profile: "PatientProfile") -> str:
        """生成首次主诉"""
        first_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个患者，需要向医生描述你的情况。"),
            ("user", """你有以下主要症状：{symptoms}。

请用一句话简要地向医生说明你的情况，不要说得太专业，像普通患者一样。
例如："医生您好，我最近有点..."
""")
        ])
        
        chain = first_prompt | self.llm
        result = await chain.ainvoke({
            "symptoms": "、".join(profile.primary_symptoms)
        })
        
        return result.content
    
    async def answer_question(
        self,
        question: str,
        disease_name: str,
        profile: "PatientProfile"
    ) -> str:
        """回答医生问题"""
        chain = self.prompt | self.llm
        
        result = await chain.ainvoke({
            "disease": disease_name,
            "primary_symptoms": "、".join(profile.primary_symptoms),
            "secondary_symptoms": "、".join(profile.secondary_symptoms),
            "age": profile.age,
            "gender": profile.gender,
            "duration": profile.duration,
            "question": question
        })
        
        return result.content
```

#### 5.4.3 结果判断 Agent

**文件**: `app/agents/result_analyzer.py`

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class DiagnosisResult(BaseModel):
    """诊断结果"""
    diagnosis: str = Field(description="诊断疾病名称")
    is_correct: bool = Field(description="是否与目标疾病一致")
    confidence: float = Field(description="置信度")
    reason: str = Field(description="判断理由")


class ResultAnalyzerAgent:
    """结果判断 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        self.parser = PydanticOutputParser(pydantic_object=DiagnosisResult)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个医学分析专家。你的任务是从医生的回复中提取诊断结果，并判断是否与目标疾病一致。

{format_instructions}"""),
            ("user", """医生的回复：
"""
{doctor_response}
"""

目标疾病：{target_disease}

请分析：
1. 提取医生诊断的疾病名称
2. 判断是否与目标疾病一致（包含也算正确，例如目标是"感冒"，诊断是"普通感冒"也算正确）
3. 给出置信度（0-1之间）
4. 解释判断理由
""")
        ])
    
    async def analyze(
        self,
        doctor_response: str,
        target_disease: str
    ) -> DiagnosisResult:
        """分析诊断结果"""
        chain = self.prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "doctor_response": doctor_response,
            "target_disease": target_disease,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result
```
```

---

### 4.2 Token 管理模块

**文件**: `app/services/token_manager.py`

**功能**:
- 自动获取 Token
- Token 过期检测
- 自动刷新

**实现思路**:
```python
from datetime import datetime, timedelta
import httpx
from app.models import ApiToken

class TokenManager:
    """Token 管理器"""
    
    BASE_URL = "https://centerapi.qschou.com"
    
    async def get_valid_token(self) -> str:
        """获取有效的 Token"""
        # 检查数据库中是否有未过期的 Token
        token = ApiToken.select().where(
            ApiToken.is_active == True,
            ApiToken.expires_at > datetime.now()
        ).order_by(ApiToken.created_at.desc()).first()
        
        if token:
            return token.access_token
        
        # 没有有效 Token，重新获取
        return await self._fetch_new_token()
    
    async def _fetch_new_token(self) -> str:
        """获取新 Token"""
        async with httpx.AsyncClient() as client:
            # 第一步：发送短信验证码登录
            step1_data = {
                "country_code": "CN",
                "phone": "18226287291",
                "sms_code": "9527",
                "auth_key": "qsevidence_pc"
            }
            
            resp1 = await client.post(
                f"{self.BASE_URL}/passport/sms/login",
                json=step1_data
            )
            resp1_data = resp1.json()
            
            # 获取 random_num
            user_list = resp1_data['data']['user_list']
            random_num = user_list[0]['random_num']
            
            # 第二步：获取 access_token
            step2_data = {"random_num": random_num}
            resp2 = await client.post(
                f"{self.BASE_URL}/passport/phone-multi-user",
                json=step2_data
            )
            resp2_data = resp2.json()
            
            access_token = resp2_data['data']['access_token']
            refresh_token = resp2_data['data']['refresh_token']
            expires_in = int(resp2_data['data']['expires_in'])
            
            # 保存到数据库
            ApiToken.create(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                expires_at=datetime.now() + timedelta(seconds=expires_in)
            )
            
            return access_token
```

---

### 4.3 医生接口调用模块

**文件**: `app/services/doctor_service.py`

**功能**:
- 调用医生 API
- 处理 SSE 流式响应
- 提取医生问题和诊断

**实现思路**:
```python
import httpx
from typing import AsyncGenerator, Dict

class DoctorService:
    """医生接口服务"""
    
    API_URL = "https://test-chatgpt-api.qschou.com/qsevidence/session/stream"
    
    async def ask_doctor(
        self, 
        message: str, 
        session_id: str = "",
        token: str = None
    ) -> Dict:
        """向医生提问（非深度模式）"""
        headers = {
            "qsc-token": token,
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "ask",
            "session_id": session_id,
            "message": message,
            "is_deep_research": False
        }
        
        response_text = ""
        doctor_session_id = session_id
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", self.API_URL, json=data, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        try:
                            event_data = json.loads(data_str)
                            
                            # 提取 session_id
                            if not doctor_session_id and 'session_id' in event_data:
                                doctor_session_id = event_data['session_id']
                            
                            # 累积响应内容
                            if 'chunk' in event_data:
                                response_text += event_data['chunk']
                        except:
                            pass
        
        return {
            "session_id": doctor_session_id,
            "message": response_text.strip(),
            "raw_response": response_text
        }
```

---

### 4.4 患者 Agent 模块

**文件**: `app/agents/patient_agent.py`

**功能**:
- 根据症状列表生成回答
- 使用 LangChain 进行智能回复

**实现思路**:
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List

class PatientAgent:
    """患者 Agent - 模拟患者回答"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个患有{disease}的患者，症状包括：{symptoms}。
            
现在医生向你提问，请根据你的症状如实回答。
- 如果医生问到的症状在你的症状列表中，明确回答"有"
- 如果不在列表中，回答"没有"或"不太确定"
- 回答要自然、口语化，像真实患者一样
- 回答要简洁，每次回答不超过50字
- 对于年龄、性别等基本信息，可以合理推测"""),
            ("user", "医生的问题：{question}")
        ])
    
    async def answer_question(
        self, 
        question: str, 
        disease_name: str, 
        symptoms: List[str]
    ) -> str:
        """回答医生的问题"""
        symptoms_str = "、".join(symptoms)
        
        chain = self.prompt | self.llm
        
        response = await chain.ainvoke({
            "disease": disease_name,
            "symptoms": symptoms_str,
            "question": question
        })
        
        return response.content
```

---

### 4.5 测试控制器

**文件**: `app/controllers/test_controller.py`

**功能**:
- 启动测试流程
- 管理对话轮次
- 结果比对

**实现思路**:
```python
import uuid
from app.models import Disease, TestSession, Conversation
from app.services.token_manager import TokenManager
from app.services.doctor_service import DoctorService
from app.agents.patient_agent import PatientAgent

class TestController:
    """测试控制器"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.doctor_service = DoctorService()
        self.patient_agent = PatientAgent()
    
    async def start_test(self, disease_id: int, max_rounds: int = 10) -> str:
        """启动测试"""
        # 创建测试会话
        session_id = f"test-{uuid.uuid4()}"
        disease = Disease.get_by_id(disease_id)
        
        test_session = TestSession.create(
            session_id=session_id,
            disease_id=disease,
            status='running'
        )
        
        # 获取疾病症状
        symptoms = [ds.symptom.name for ds in disease.symptoms]
        
        # 获取 Token
        token = await self.token_manager.get_valid_token()
        
        # 首次对话
        first_message = f"医生您好，我有点不舒服"
        doctor_session_id = ""
        
        for round_num in range(max_rounds):
            if round_num == 0:
                # 第一轮：患者主诉
                patient_message = first_message
            else:
                # 后续轮次：根据医生问题回答
                patient_message = await self.patient_agent.answer_question(
                    question=doctor_response['message'],
                    disease_name=disease.name,
                    symptoms=symptoms
                )
            
            # 记录患者消息
            Conversation.create(
                session_id=test_session,
                round=round_num + 1,
                role='patient',
                message=patient_message
            )
            
            # 调用医生接口
            doctor_response = await self.doctor_service.ask_doctor(
                message=patient_message,
                session_id=doctor_session_id,
                token=token
            )
            
            doctor_session_id = doctor_response['session_id']
            
            # 记录医生消息
            Conversation.create(
                session_id=test_session,
                round=round_num + 1,
                role='doctor',
                message=doctor_response['message'],
                raw_response=doctor_response['raw_response']
            )
            
            # 检查是否包含诊断结果
            if self._is_diagnosis_complete(doctor_response['message']):
                break
        
        # 更新会话
        test_session.doctor_session_id = doctor_session_id
        test_session.status = 'completed'
        test_session.completed_at = datetime.now()
        
        # 提取并比对诊断结果
        await self._extract_and_compare_diagnosis(test_session, disease)
        
        test_session.save()
        
        return session_id
    
    def _is_diagnosis_complete(self, message: str) -> bool:
        """判断医生是否给出诊断"""
        keywords = ['诊断', '可能是', '考虑', '建议']
        return any(kw in message for kw in keywords)
    
    async def _extract_and_compare_diagnosis(self, test_session, disease):
        """提取并比对诊断结果"""
        # 获取最后一轮医生的回复
        last_doctor_msg = Conversation.select().where(
            Conversation.session_id == test_session,
            Conversation.role == 'doctor'
        ).order_by(Conversation.round.desc()).first()
        
        if not last_doctor_msg:
            return
        
        # 使用 LLM 提取诊断疾病
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        prompt = f"""从以下医生的回复中提取诊断的疾病名称，只返回疾病名称，不要其他内容：

{last_doctor_msg.message}

如果没有明确的疾病诊断，返回"未诊断"。"""
        
        response = await llm.ainvoke(prompt)
        diagnosis = response.content.strip()
        
        # 比对结果
        is_correct = disease.name in diagnosis or diagnosis in disease.name
        
        test_session.diagnosis_result = diagnosis
        test_session.is_correct = is_correct
```

---

## 5. API 接口设计

### 5.1 测试相关接口

**文件**: `app/api/v1/test/tests.py`

#### 5.1.1 启动测试

```python
@router.post("/tests/start", summary="启动测试")
async def start_test(disease_id: int):
    """启动一次测试"""
    controller = TestController()
    session_id = await controller.start_test(disease_id)
    return Success(data={"session_id": session_id})
```

#### 5.1.2 获取测试结果

```python
@router.get("/tests/{session_id}", summary="获取测试结果")
async def get_test_result(session_id: str):
    """获取测试结果"""
    session = TestSession.get(TestSession.session_id == session_id)
    
    # 获取对话历史
    conversations = list(
        Conversation.select()
        .where(Conversation.session_id == session)
        .order_by(Conversation.round)
    )
    
    return Success(data={
        "session_id": session.session_id,
        "disease": session.disease_id.name,
        "diagnosis": session.diagnosis_result,
        "is_correct": session.is_correct,
        "status": session.status,
        "conversations": [
            {
                "round": c.round,
                "role": c.role,
                "message": c.message
            } for c in conversations
        ]
    })
```

#### 5.1.3 获取测试列表

```python
@router.post("/tests/all/", summary="获取测试列表")
async def get_test_list(current: int = 1, size: int = 10):
    """获取测试列表"""
    query = TestSession.select().order_by(TestSession.started_at.desc())
    total = query.count()
    
    sessions = list(query.paginate(current, size))
    
    return SuccessExtra(
        data={
            "records": [
                {
                    "session_id": s.session_id,
                    "disease": s.disease_id.name,
                    "diagnosis": s.diagnosis_result,
                    "is_correct": s.is_correct,
                    "status": s.status,
                    "started_at": s.started_at.isoformat()
                } for s in sessions
            ]
        },
        total=total,
        current=current,
        size=size
    )
```

### 5.2 疾病管理接口

**文件**: `app/api/v1/test/diseases.py`

```python
@router.get("/diseases/random", summary="随机获取疾病")
async def get_random_disease():
    """随机获取一个疾病"""
    disease = Disease.select().order_by(fn.Random()).first()
    
    symptoms = [ds.symptom.name for ds in disease.symptoms]
    
    return Success(data={
        "id": disease.id,
        "name": disease.name,
        "symptoms": symptoms
    })

@router.post("/diseases/all/", summary="获取疾病列表")
async def get_diseases(name: str = None, current: int = 1, size: int = 10):
    """获取疾病列表"""
    query = Disease.select()
    if name:
        query = query.where(Disease.name.contains(name))
    
    total = query.count()
    diseases = list(query.order_by(Disease.name).paginate(current, size))
    
    return SuccessExtra(
        data={
            "records": [
                {
                    "id": d.id,
                    "name": d.name,
                    "symptom_count": len(d.symptoms)
                } for d in diseases
            ]
        },
        total=total,
        current=current,
        size=size
    )
```

---

## 6. 前端实现

### 6.1 页面结构

```
web/src/views/test/
├── index.vue                 # 测试列表页
├── detail/
│   └── [sessionId].vue       # 测试详情页（对话展示）
└── start.vue                 # 启动测试页
```

### 6.2 测试启动页面

**文件**: `web/src/views/test/start.vue`

**功能**:
- 选择疾病
- 启动测试
- 实时显示对话过程（可选）

**关键代码**:
```vue
<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NCard, NSelect, NAlert } from 'naive-ui';
import { fetchGetRandomDisease, fetchStartTest } from '@/service/api';
import { useRouterPush } from '@/hooks/common/router';

const { routerPush } = useRouterPush();

const selectedDisease = ref<any>(null);
const loading = ref(false);

// 随机获取疾病
async function getRandomDisease() {
  const { data } = await fetchGetRandomDisease();
  selectedDisease.value = data;
}

// 启动测试
async function startTest() {
  if (!selectedDisease.value) {
    window.$message?.warning('请先选择疾病');
    return;
  }
  
  loading.value = true;
  try {
    const { data } = await fetchStartTest(selectedDisease.value.id);
    window.$message?.success('测试已启动');
    
    // 跳转到详情页
    routerPush({
      name: 'test_detail',
      params: { sessionId: data.session_id }
    });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="p-16px">
    <NCard title="启动测试">
      <div class="mb-16px">
        <NButton type="primary" @click="getRandomDisease">
          随机选择疾病
        </NButton>
      </div>
      
      <NAlert v-if="selectedDisease" type="info" class="mb-16px">
        <div>疾病：{{ selectedDisease.name }}</div>
        <div>症状：{{ selectedDisease.symptoms.join('、') }}</div>
      </NAlert>
      
      <NButton 
        type="success" 
        :loading="loading" 
        :disabled="!selectedDisease"
        @click="startTest"
      >
        开始测试
      </NButton>
    </NCard>
  </div>
</template>
```

### 6.3 测试详情页面

**文件**: `web/src/views/test/detail/[sessionId].vue`

**功能**:
- 展示对话历史
- 显示诊断结果
- 结果对比

**关键代码**:
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { NCard, NTimeline, NTimelineItem, NTag, NAlert } from 'naive-ui';
import { fetchGetTestResult } from '@/service/api';

const route = useRoute();
const sessionId = route.params.sessionId as string;

const testResult = ref<any>(null);
const loading = ref(false);

async function loadResult() {
  loading.value = true;
  try {
    const { data } = await fetchGetTestResult(sessionId);
    testResult.value = data;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadResult();
});
</script>

<template>
  <div class="p-16px">
    <NCard v-if="testResult" title="测试结果">
      <!-- 结果摘要 -->
      <div class="mb-16px">
        <div>目标疾病：<strong>{{ testResult.disease }}</strong></div>
        <div>医生诊断：<strong>{{ testResult.diagnosis }}</strong></div>
        <div>
          诊断结果：
          <NTag :type="testResult.is_correct ? 'success' : 'error'">
            {{ testResult.is_correct ? '正确' : '错误' }}
          </NTag>
        </div>
      </div>
      
      <!-- 对话历史 -->
      <NCard title="对话历史" size="small">
        <NTimeline>
          <NTimelineItem
            v-for="conv in testResult.conversations"
            :key="`${conv.round}-${conv.role}`"
            :type="conv.role === 'patient' ? 'success' : 'info'"
          >
            <template #header>
              <span class="font-bold">
                {{ conv.role === 'patient' ? '患者' : '医生' }}
              </span>
            </template>
            <div class="whitespace-pre-wrap">{{ conv.message }}</div>
          </NTimelineItem>
        </NTimeline>
      </NCard>
    </NCard>
  </div>
</template>
```

---

## 7. 实施步骤（基于现有架构）

### 第一阶段：数据模型和数据导入（2-3小时）

#### 任务清单:
- [ ] 扩展 Agent 模型（添加 langchain_config, prompt_template, tools 字段）
- [ ] 创建 AgentRelation 模型（Agent 关联关系）
- [ ] 创建医疗相关模型（Disease, Symptom, DiseaseSymptom）
- [ ] 创建测试执行模型（TestExecution, ExecutionStep, Conversation）
- [ ] 创建 ApiToken 模型
- [ ] 运行数据库迁移：`aerich migrate --name add_medical_models`
- [ ] 编写数据导入脚本（`app/services/data_import.py`）
- [ ] 导入 CMB-Clin-summary.xlsx 数据
- [ ] 验证数据完整性

**涉及文件**:
```
app/models/
├── system/
│   └── agent.py              # 扩展现有模型
└── medical/                   # 新建目录
    ├── __init__.py
    ├── disease.py            # 疾病、症状模型
    ├── test_execution.py     # 测试执行模型
    └── api_token.py          # Token模型

app/services/
└── data_import.py            # 数据导入服务

migrations/models/
└── xxx_add_medical_models.py  # 迁移文件
```

---

### 第二阶段：Agent 配置和基础服务（4-5小时）

#### 任务清单:
- [ ] 安装 LangChain 相关依赖
- [ ] 配置 OpenAI API Key（.env 文件）
- [ ] 实现 Token 管理服务（`app/services/token_manager.py`）
- [ ] 实现医生接口调用服务（`app/services/doctor_service.py`）
- [ ] 在数据库中配置 4 个 Agent：
  - [ ] 医疗测试主控Agent（business类型）
  - [ ] 症状分析Agent（function类型）
  - [ ] 患者对话Agent（function类型）
  - [ ] 结果判断Agent（function类型）
- [ ] 配置 Agent 关联关系（AgentRelation 表）

**涉及文件**:
```
app/services/
├── token_manager.py         # Token管理
└── doctor_service.py        # 医生接口

.env
# 添加配置
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1

requirements.txt
# 添加依赖
langchain>=0.1.0
langchain-openai>=0.0.5
httpx>=0.25.0
pandas>=2.0.0
openpyxl>=3.1.0
```

**Agent 配置示例**（通过 SQL 或 API 插入）:
```sql
-- 主控 Agent
INSERT INTO agents (name, agent_type, description, config, langchain_config, prompt_template)
VALUES (
  '医疗测试主控Agent',
  'business',
  '协调整个测试流程',
  '{"max_rounds": 10, "timeout": 300}',
  '{"model": "gpt-3.5-turbo", "temperature": 0.3}',
  '你是一个医疗测试协调员...'
);
```

---

### 第三阶段：Agent 实现（5-6小时）

#### 任务清单:
- [ ] 实现症状分析 Agent（`app/agents/symptom_analyzer.py`）
- [ ] 实现患者对话 Agent（`app/agents/patient_dialog.py`）
- [ ] 实现结果判断 Agent（`app/agents/result_analyzer.py`）
- [ ] 实现主控 Agent（`app/agents/master_agent.py`）
- [ ] 实现测试执行控制器（`app/controllers/test_execution.py`）
- [ ] 测试 Agent 独立运行
- [ ] 测试 Agent 协作流程

**涉及文件**:
```
app/agents/                   # 新建目录
├── __init__.py
├── symptom_analyzer.py      # 症状分析 Agent
├── patient_dialog.py        # 患者对话 Agent
├── result_analyzer.py       # 结果判断 Agent
└── master_agent.py          # 主控 Agent

app/controllers/
└── test_execution.py        # 测试执行控制器
```

---

### 第四阶段：API 接口（3-4小时）

#### 任务清单:
- [ ] 创建测试相关 Schema（`app/schemas/test_execution.py`）
- [ ] 实现测试 API 路由（`app/api/v1/medical/tests.py`）
- [ ] 实现疾病管理 API（`app/api/v1/medical/diseases.py`）
- [ ] 实现 Agent 配置 API（`app/api/v1/medical/agents.py`）
- [ ] 注册路由到主应用
- [ ] 测试 API 接口

**涉及文件**:
```
app/schemas/
└── test_execution.py        # 测试执行 Schema

app/api/v1/medical/           # 新建目录
├── __init__.py
├── tests.py                 # 测试 API
├── diseases.py              # 疾病 API
└── agents.py                # Agent 配置 API

app/api/v1/__init__.py       # 注册路由
```

**主要 API**:
```
POST   /api/v1/medical/tests/start          # 启动测试
GET    /api/v1/medical/tests/{execution_id}  # 获取测试结果
POST   /api/v1/medical/tests/all/            # 获取测试列表
GET    /api/v1/medical/diseases/random       # 随机获取疾病
POST   /api/v1/medical/diseases/all/         # 获取疾病列表
POST   /api/v1/medical/agents/all/           # 获取 Agent 列表
```

---

### 第五阶段：前端页面（4-5小时）

#### 任务清单:
- [ ] 创建 Agent 配置页面（复用现有 Agent 页面）
- [ ] 创建测试启动页面
- [ ] 创建测试执行监控页面（实时展示对话）
- [ ] 创建测试结果页面
- [ ] 创建测试列表页面
- [ ] 定义前端 API 接口
- [ ] 添加路由配置
- [ ] 添加国际化文本

**涉及文件**:
```
web/src/views/medical/        # 新建目录
├── agent/
│   └── index.vue            # Agent配置页（可复用现有）
├── test/
│   ├── start.vue            # 测试启动页
│   ├── monitor.vue          # 执行监控页
│   ├── result/
│   │   └── [id].vue         # 测试结果页
│   └── index.vue            # 测试列表页

web/src/service/api/
└── medical.ts               # 医疗测试 API

web/src/typings/
└── api.d.ts                 # 添加 Api.Medical 命名空间

web/src/locales/langs/
├── zh-cn.ts                 # 中文
└── en-us.ts                 # 英文
```

---

### 第六阶段：测试和优化（2-3小时）

#### 任务清单:
- [ ] 端到端测试（完整流程）
- [ ] 测试 LangChain Agent 准确性
- [ ] 测试医生接口稳定性
- [ ] 优化 Prompt 模板
- [ ] 异常处理和重试机制
- [ ] 性能优化（缓存、并发）
- [ ] 日志完善
- [ ] Bug 修复

**测试用例**:
1. 从数据库随机选择疾病
2. 启动测试
3. 观察 Agent 协作过程
4. 检查对话是否自然
5. 验证诊断结果准确性
6. 查看执行日志

---

## 8. 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 1 | 数据模型和数据导入 | 2-3 小时 |
| 2 | Agent配置和基础服务 | 4-5 小时 |
| 3 | Agent实现 | 5-6 小时 |
| 4 | API接口 | 3-4 小时 |
| 5 | 前端页面 | 4-5 小时 |
| 6 | 测试和优化 | 2-3 小时 |
| **总计** | | **20-26 小时** |

---

## 9. 环境配置

### 9.1 环境变量（.env）

```bash
# OpenAI API
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1

# 医生 API
DOCTOR_API_URL=https://test-chatgpt-api.qschou.com
DOCTOR_API_PHONE=18226287291
DOCTOR_API_SMS_CODE=9527

# 数据库（使用现有配置）
DB_URL=postgres://user:pass@localhost:5432/dbname
```

### 9.2 依赖安装

```bash
# 后端
cd /path/to/fast-soy
pdm add langchain langchain-openai httpx pandas openpyxl

# 或使用 requirements.txt
echo "langchain>=0.1.0" >> requirements.txt
echo "langchain-openai>=0.0.5" >> requirements.txt
echo "httpx>=0.25.0" >> requirements.txt
echo "pandas>=2.0.0" >> requirements.txt
echo "openpyxl>=3.1.0" >> requirements.txt
pdm install

# 前端（已有依赖）
cd web
pnpm install
```

---

## 10. 快速启动指南

### 10.1 初始化数据

```bash
# 1. 运行数据库迁移
aerich migrate --name add_medical_models
aerich upgrade

# 2. 导入疾病数据
python scripts/import_disease_data.py

# 3. 配置 Agent（通过数据库或 API）
python scripts/init_agents.py
```

### 10.2 启动服务

```bash
# 启动后端
python run.py

# 启动前端
cd web
pnpm dev
```

### 10.3 运行测试

```bash
# 通过 API 启动测试
curl -X POST "http://localhost:8000/api/v1/medical/tests/start" \
  -H "Content-Type: application/json" \
  -d '{"disease_id": 1}'

# 或访问前端页面
# http://localhost:3000/medical/test/start
```

---

## 11. 注意事项

### 11.1 LangChain 集成风险

- ⚠️ **学习曲线**：LangChain 相对较新，需要预留调研时间
- ⚠️ **超时处理**：LLM 调用可能超时，需要重试机制
- ⚠️ **成本控制**：监控 API 调用次数和 Token 使用量
- ⚠️ **本地模型备选**：考虑使用 Ollama 等本地模型降低成本

### 11.2 医生 API 限制

- ⚠️ 注意调用频率限制
- ⚠️ Token 过期时间（提前 5 分钟刷新）
- ⚠️ SSE 流式响应解析（处理心跳包）

### 11.3 数据库性能

- ✅ 使用 Tortoise ORM 的 `prefetch_related` 避免 N+1 查询
- ✅ 对话记录表需要添加索引（execution_id, round）
- ✅ 考虑定期清理历史数据

### 11.4 前端实时更新

- 💡 考虑使用 WebSocket 实时推送执行状态
- 💡 使用轮询作为备选方案
- 💡 执行过程可视化（流程图）

---

## 12. 验收标准

### 功能验收

- [ ] 能成功导入疾病数据（至少50条）
- [ ] Token 自动获取和刷新正常
- [ ] 4个 Agent 配置完整并能独立运行
- [ ] 主控 Agent 能正确协调子 Agent
- [ ] 患者 Agent 回答符合症状
- [ ] 医生接口调用成功率 > 90%
- [ ] 对话历史完整记录
- [ ] 诊断结果准确提取
- [ ] 结果比对逻辑正确
- [ ] 前端页面正常展示

### 性能验收

- [ ] 单次测试完成时间 < 3 分钟
- [ ] LLM 调用响应时间 < 10 秒
- [ ] 数据库查询响应 < 100ms
- [ ] 支持同时进行 3 个测试

### 质量验收

- [ ] 代码符合项目规范（使用现有的 CRUD、Schema 模式）
- [ ] 关键操作有日志记录
- [ ] 异常处理完善（超时、重试、降级）
- [ ] API 返回格式统一（Success/SuccessExtra）
- [ ] 前端使用现有组件库（Naive UI）

### 第一阶段：数据准备（预计 2 小时）

#### 任务清单:
- [ ] 创建数据库表结构（Peewee 模型）
- [ ] 编写数据导入脚本
- [ ] 导入 CMB-Clin-summary.xlsx 数据
- [ ] 验证数据完整性

**文件清单**:
```
app/models/
├── __init__.py
├── base.py          # Peewee 基础配置
├── disease.py       # Disease, Symptom, DiseaseSymptom
└── test.py          # TestSession, Conversation, ApiToken
```

---

### 第二阶段：核心服务（预计 4 小时）

#### 任务清单:
- [ ] Token 管理服务
- [ ] 医生接口调用服务
- [ ] 患者 Agent 实现（LangChain）
- [ ] 测试控制器实现

**文件清单**:
```
app/services/
├── token_manager.py
├── doctor_service.py
└── data_import.py

app/agents/
└── patient_agent.py

app/controllers/
└── test_controller.py
```

---

### 第三阶段：API 接口（预计 2 小时）

#### 任务清单:
- [ ] 测试相关 API
- [ ] 疾病管理 API
- [ ] 路由注册

**文件清单**:
```
app/api/v1/test/
├── __init__.py
├── tests.py
└── diseases.py
```

---

### 第四阶段：前端页面（预计 3 小时）

#### 任务清单:
- [ ] 测试启动页面
- [ ] 测试列表页面
- [ ] 测试详情页面
- [ ] API 接口定义

**文件清单**:
```
web/src/views/test/
├── index.vue
├── start.vue
└── detail/
    └── [sessionId].vue

web/src/service/api/
└── test.ts

web/src/typings/
└── api.d.ts  # 添加 Api.Test 命名空间
```

---

### 第五阶段：测试和优化（预计 2 小时）

#### 任务清单:
- [ ] 端到端测试
- [ ] 修复 Bug
- [ ] 性能优化
- [ ] 文档完善

---

## 8. 环境配置

### 8.1 后端依赖

**文件**: `requirements.txt`（追加）

```txt
peewee>=3.17.0
pandas>=2.0.0
openpyxl>=3.1.0
langchain>=0.1.0
langchain-openai>=0.0.5
httpx>=0.25.0
```

### 8.2 环境变量

**文件**: `.env`（追加）

```bash
# OpenAI API
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1  # 或使用代理

# 数据库
DATABASE_PATH=./data/test.db

# 医生 API
DOCTOR_API_URL=https://test-chatgpt-api.qschou.com
DOCTOR_API_PHONE=18226287291
DOCTOR_API_SMS_CODE=9527
```

---

## 9. 目录结构

```
fast-soy/
├── app/
│   ├── models/
│   │   ├── disease.py          # 疾病模型
│   │   └── test.py             # 测试模型
│   ├── services/
│   │   ├── token_manager.py    # Token 管理
│   │   ├── doctor_service.py   # 医生接口
│   │   └── data_import.py      # 数据导入
│   ├── agents/
│   │   └── patient_agent.py    # 患者 Agent
│   ├── controllers/
│   │   └── test_controller.py  # 测试控制器
│   ├── api/v1/test/
│   │   ├── __init__.py
│   │   ├── tests.py            # 测试 API
│   │   └── diseases.py         # 疾病 API
│   └── schemas/
│       └── tests.py            # 测试 Schema
├── web/src/
│   ├── views/test/
│   │   ├── index.vue
│   │   ├── start.vue
│   │   └── detail/
│   │       └── [sessionId].vue
│   ├── service/api/
│   │   └── test.ts
│   └── typings/
│       └── api.d.ts
├── data/
│   ├── test.db                 # SQLite 数据库
│   └── CMB-Clin-summary.xlsx   # 原始数据
└── scripts/
    └── import_data.py          # 数据导入脚本
```

---

## 10. 关键技术点

### 10.1 SSE 流式响应处理

医生 API 返回的是 Server-Sent Events (SSE) 格式，需要正确解析：

```python
async with httpx.AsyncClient() as client:
    async with client.stream("POST", url, json=data, headers=headers) as response:
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_str = line[5:].strip()
                event_data = json.loads(data_str)
                # 处理事件数据
```

### 10.2 LangChain Agent 配置

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)
```

### 10.3 Peewee 多对多关系

```python
# 查询疾病的所有症状
disease = Disease.get_by_id(1)
symptoms = [ds.symptom for ds in disease.symptoms]

# 查询症状关联的所有疾病
symptom = Symptom.get_by_id(1)
diseases = [ds.disease for ds in symptom.diseases]
```

---

## 11. 注意事项

### 11.1 Token 管理

- ✅ Token 有过期时间，需要定时刷新
- ✅ 建议提前 5 分钟刷新 Token
- ✅ 并发请求时要注意 Token 共享

### 11.2 医生 API 限流

- ⚠️ 注意 API 调用频率限制
- ⚠️ 建议加入请求间隔（1-2秒）
- ⚠️ 失败重试机制

### 11.3 LLM 成本控制

- 💰 使用 gpt-3.5-turbo 降低成本
- 💰 限制 max_tokens
- 💰 记录 Token 使用量

### 11.4 数据质量

- 📊 导入数据前验证格式
- 📊 症状文本需要清洗（去重、标准化）
- 📊 建议人工审核部分数据

---

## 12. 后续扩展方向

### 12.1 功能扩展

- 🚀 支持深度搜索模式
- 🚀 添加主控 Agent 规划
- 🚀 多 Agent 协作
- 🚀 批量测试功能
- 🚀 测试报告生成

### 12.2 性能优化

- ⚡ 使用 Redis 缓存 Token
- ⚡ 异步任务队列（RQ）
- ⚡ 数据库索引优化

### 12.3 UI 增强

- 🎨 实时对话流展示
- 🎨 统计图表（准确率、常见错误）
- 🎨 对话过程可视化

---

## 13. 验收标准

### 功能验收

- [ ] 能成功导入疾病数据
- [ ] Token 自动获取和刷新正常
- [ ] 患者 Agent 能根据症状回答问题
- [ ] 医生接口调用成功
- [ ] 对话历史完整记录
- [ ] 诊断结果正确提取和比对
- [ ] 前端页面正常展示

### 性能验收

- [ ] 单次测试完成时间 < 2 分钟
- [ ] 支持同时进行 3 个测试
- [ ] 数据库查询响应 < 100ms

### 质量验收

- [ ] 代码符合项目规范
- [ ] 关键功能有日志记录
- [ ] 异常处理完善
- [ ] API 返回格式统一

---

## 14. 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| 1 | 数据准备 | 2 小时 |
| 2 | 核心服务 | 4 小时 |
| 3 | API 接口 | 2 小时 |
| 4 | 前端页面 | 3 小时 |
| 5 | 测试优化 | 2 小时 |
| **总计** | | **13 小时** |

---

**文档版本**: 1.0  
**最后更新**: 2025-11-06
