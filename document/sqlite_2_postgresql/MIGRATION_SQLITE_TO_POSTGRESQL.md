# SQLite 迁移到 PostgreSQL 详细文档

## 📋 目录

1. [迁移概述](#迁移概述)
2. [前置准备](#前置准备)
3. [需要修改的文件清单](#需要修改的文件清单)
4. [详细修改步骤](#详细修改步骤)
5. [数据迁移](#数据迁移)
6. [测试验证](#测试验证)
7. [常见问题](#常见问题)

---

## 迁移概述

本文档详细说明如何将 FastSoyAdmin 项目从 SQLite 数据库迁移到 PostgreSQL 数据库。

### 主要变更点

1. **依赖包变更**：从 `aiosqlite` 迁移到 PostgreSQL 驱动
2. **数据库连接配置**：从文件路径改为连接字符串
3. **SQL 语法差异**：修复 SQLite 特定的 SQL 语法
4. **自增 ID 处理**：从 SQLite 的 `AUTOINCREMENT` 改为 PostgreSQL 的序列
5. **工具脚本修改**：更新数据库维护脚本

---

## 前置准备

### 1. PostgreSQL 环境准备

确保本地已安装并运行 PostgreSQL：

```bash
# macOS (使用 Homebrew)
brew install postgresql@14
brew services start postgresql@14

# 验证 PostgreSQL 是否运行
psql --version
```

### 2. 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE DATABASE fast_soy_admin;
CREATE USER fast_soy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fast_soy_admin TO fast_soy_user;
\q
```

### 3. 备份现有 SQLite 数据（可选）

如果已有数据需要迁移：

```bash
# 备份 SQLite 数据库
cp app_system.sqlite3 app_system.sqlite3.backup
```

---

## 需要修改的文件清单

### 核心配置文件

1. ✅ `pyproject.toml` - 依赖包配置
2. ✅ `app/settings/config.py` - 数据库连接配置
3. ✅ `migrations/app_system/0_20251106095928_init.py` - 初始化迁移文件
4. ✅ `cron_reset.py` - 数据库重置脚本

### 可选文件（Docker 部署）

5. ⚠️ `docker-compose.yml` - 如需添加 PostgreSQL 服务

---

## 详细修改步骤

### 步骤 1: 修改依赖包配置

**文件**: `pyproject.toml`

**修改前**:
```toml
dependencies = [
    "tortoise-orm[aiosqlite]>=0.20.1",
    # ... 其他依赖
]
```

**修改后**:
```toml
dependencies = [
    "tortoise-orm[asyncpg]>=0.20.1",  # 使用 asyncpg 作为 PostgreSQL 驱动
    # 或者使用: "tortoise-orm[psycopg]>=0.20.1"  # psycopg3 驱动
    # ... 其他依赖
]
```

**说明**:
- `asyncpg` 是异步 PostgreSQL 驱动，性能更好，推荐使用
- `psycopg` 是传统的 PostgreSQL 驱动，兼容性更好

**更新依赖**:
```bash
# 使用 PDM
pdm install

# 或使用 pip
pip install -r requirements.txt
```

---

### 步骤 2: 修改数据库连接配置

**文件**: `app/settings/config.py`

#### 2.1 修改 `tortoise_orm_factory()` 函数

**修改前**:
```python
def tortoise_orm_factory() -> dict[str, Any]:
    return {
        "connections": {
            "conn_system": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": "app_system.sqlite3"}
            }
        },
        "apps": {
            "app_system": {"models": ["app.models.system", "aerich.models"], "default_connection": "conn_system"}
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai"
    }
```

**修改后**:
```python
def tortoise_orm_factory() -> dict[str, Any]:
    return {
        "connections": {
            "conn_system": {
                "engine": "tortoise.backends.asyncpg",  # 使用 asyncpg
                # 或者使用: "engine": "tortoise.backends.psycopg",  # 使用 psycopg
                "credentials": {
                    "host": "localhost",
                    "port": "5432",
                    "user": "fast_soy_user",
                    "password": "your_password",
                    "database": "fast_soy_admin",
                }
            }
        },
        "apps": {
            "app_system": {"models": ["app.models.system", "aerich.models"], "default_connection": "conn_system"}
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai"
    }
```

#### 2.2 使用环境变量（推荐）

为了更好的配置管理，建议使用环境变量：

**修改 `Settings` 类**:
```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # 新增 PostgreSQL 配置项
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "fast_soy_user"
    DB_PASSWORD: str = "your_password"
    DB_NAME: str = "fast_soy_admin"
    
    # 修改 tortoise_orm_factory 使用配置
    @staticmethod
    def tortoise_orm_factory(host: str, port: int, user: str, password: str, database: str) -> dict[str, Any]:
        return {
            "connections": {
                "conn_system": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": host,
                        "port": port,
                        "user": user,
                        "password": password,
                        "database": database,
                    }
                }
            },
            "apps": {
                "app_system": {"models": ["app.models.system", "aerich.models"], "default_connection": "conn_system"}
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai"
        }
    
    # 修改 TORTOISE_ORM 属性
    @property
    def TORTOISE_ORM(self) -> dict[str, Any]:
        return self.tortoise_orm_factory(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DB_NAME
        )
```

**创建 `.env` 文件**（在项目根目录）:
```env
# PostgreSQL 配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=fast_soy_user
DB_PASSWORD=your_password
DB_NAME=fast_soy_admin
```

---

### 步骤 3: 修改迁移文件

**文件**: `migrations/app_system/0_20251106095928_init.py`

这是最重要的修改，需要将 SQLite 特定的 SQL 语法改为 PostgreSQL 兼容的语法。

#### 主要 SQL 语法差异对比

| SQLite | PostgreSQL | 说明 |
|--------|------------|------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` 或 `INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY` | 自增主键 |
| `REAL` | `DOUBLE PRECISION` | 浮点数 |
| `INT NOT NULL DEFAULT 0` (布尔) | `BOOLEAN NOT NULL DEFAULT FALSE` | 布尔类型 |
| `INT NOT NULL DEFAULT 0` (数值) | `INTEGER NOT NULL DEFAULT 0` | 数值类型 |
| `/* 注释 */` | `-- 注释` | 注释语法 |

#### 修改示例

**修改前** (SQLite):
```sql
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "user_name" VARCHAR(20) NOT NULL UNIQUE,
    "multi_tab" INT NOT NULL DEFAULT 0,
    "process_time" REAL
);
```

**修改后** (PostgreSQL):
```sql
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL PRIMARY KEY NOT NULL,
    "user_name" VARCHAR(20) NOT NULL UNIQUE,
    "multi_tab" BOOLEAN NOT NULL DEFAULT FALSE,
    "process_time" DOUBLE PRECISION
);
```

#### 完整的迁移文件修改

由于迁移文件较长，主要修改点如下：

1. **所有表的 `id` 字段**:
   ```sql
   -- 修改前
   "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
   
   -- 修改后
   "id" SERIAL PRIMARY KEY NOT NULL
   ```

2. **布尔字段** (`multi_tab`, `keep_alive`, `hide_in_menu`, `props`, `constant`):
   ```sql
   -- 修改前
   "multi_tab" INT NOT NULL DEFAULT 0
   
   -- 修改后
   "multi_tab" BOOLEAN NOT NULL DEFAULT FALSE
   ```

3. **浮点数字段** (`process_time`):
   ```sql
   -- 修改前
   "process_time" REAL
   
   -- 修改后
   "process_time" DOUBLE PRECISION
   ```

4. **注释语法**:
   ```sql
   -- 修改前
   /* 用户id */
   
   -- 修改后
   -- 用户id
   ```

5. **外键约束**:
   PostgreSQL 的外键语法与 SQLite 基本相同，但建议检查语法是否正确。

**注意**: 由于迁移文件自动生成，建议：
1. 先删除现有迁移文件
2. 重新初始化数据库
3. 让 Tortoise ORM 自动生成新的 PostgreSQL 兼容的迁移文件

---

### 步骤 4: 修改数据库重置脚本

**文件**: `cron_reset.py`

**修改前**:
```python
# 获取所有表名
table_count, tables = await conn.execute_query('SELECT name FROM sqlite_master WHERE type = "table" AND name NOT LIKE "sqlite_%";')
# 删除所有表
for table in tables:
    table_name = table["name"]
    print("table_name", table_name)
    if table_name != "aerich":
        await conn.execute_query(f'delete from "{table_name}";')  # 清空数据
        await conn.execute_query(f'update sqlite_sequence SET seq = 0 where name = "{table_name}";')  # 自增长ID为0
```

**修改后**:
```python
# 获取所有表名 (PostgreSQL)
table_count, tables = await conn.execute_query("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename != 'aerich';
""")

# 删除所有表数据并重置序列
for table in tables:
    table_name = table["tablename"]
    print("table_name", table_name)
    if table_name != "aerich":
        # 清空数据
        await conn.execute_query(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
        # RESTART IDENTITY 会自动重置序列，无需单独操作
```

**完整修改后的函数**:
```python
async def init():
    await Tortoise.init(
        config=APP_SETTINGS.TORTOISE_ORM,
    )
    await Tortoise.generate_schemas()

    conn = Tortoise.get_connection("conn_system")

    # 获取所有表名 (PostgreSQL)
    table_count, tables = await conn.execute_query("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename != 'aerich';
    """)
    
    # 删除所有表数据并重置序列
    for table in tables:
        table_name = table["tablename"]
        print("table_name", table_name)
        if table_name != "aerich":
            # TRUNCATE 会清空数据并重置序列
            await conn.execute_query(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')

    await init_menus()
    await refresh_api_list()
    await init_users()

    await Tortoise.close_connections()
```

---

### 步骤 5: 更新 Docker Compose（可选）

如果使用 Docker 部署，需要添加 PostgreSQL 服务：

**文件**: `docker-compose.yml`

**添加 PostgreSQL 服务**:
```yaml
version: '3.8'

services:
  # ... 现有服务 ...
  
  postgres:
    image: postgres:14-alpine
    container_name: fast-soy-postgres
    environment:
      POSTGRES_DB: fast_soy_admin
      POSTGRES_USER: fast_soy_user
      POSTGRES_PASSWORD: your_password
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - internal
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fast_soy_user -d fast_soy_admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    # ... 现有配置 ...
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

networks:
  internal:
    driver: bridge
```

**更新 app 服务的环境变量**:
```yaml
app:
  environment:
    - LANG=zh_CN.UTF-8
    - DB_HOST=postgres
    - DB_PORT=5432
    - DB_USER=fast_soy_user
    - DB_PASSWORD=your_password
    - DB_NAME=fast_soy_admin
```

---

## 数据迁移

### 方案 1: 重新初始化（推荐用于开发环境）

如果数据不重要，可以直接重新初始化：

```bash
# 1. 确保 PostgreSQL 数据库为空
psql -U fast_soy_user -d fast_soy_admin -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 2. 运行应用，会自动初始化数据库
pdm run run.py
```

### 方案 2: 导出导入数据（用于生产环境）

#### 步骤 1: 从 SQLite 导出数据

```bash
# 安装 sqlite3-to-postgres 工具
pip install sqlite3-to-postgres

# 导出数据
sqlite3 app_system.sqlite3 .dump > sqlite_dump.sql
```

#### 步骤 2: 转换 SQL 语法

需要手动转换 SQL 语法，或者使用工具：

```bash
# 使用 pgloader (需要安装)
brew install pgloader

# 直接迁移
pgloader sqlite:///path/to/app_system.sqlite3 postgresql://fast_soy_user:password@localhost/fast_soy_admin
```

#### 步骤 3: 验证数据

```bash
psql -U fast_soy_user -d fast_soy_admin -c "SELECT COUNT(*) FROM users;"
```

---

## 测试验证

### 1. 验证数据库连接

```python
# 创建测试脚本 test_db.py
from app.settings import APP_SETTINGS
from tortoise import Tortoise, run_async

async def test_connection():
    await Tortoise.init(
        config=APP_SETTINGS.TORTOISE_ORM,
    )
    conn = Tortoise.get_connection("conn_system")
    result = await conn.execute_query("SELECT version();")
    print("PostgreSQL 版本:", result[1][0]["version"])
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(test_connection())
```

运行测试:
```bash
pdm run python test_db.py
```

### 2. 验证表结构

```bash
psql -U fast_soy_user -d fast_soy_admin -c "\dt"
```

### 3. 运行应用测试

```bash
# 启动应用
pdm run run.py

# 检查日志，确保没有数据库相关错误
```

### 4. 功能测试清单

- [ ] 用户登录
- [ ] 用户创建/更新/删除
- [ ] 角色管理
- [ ] 菜单管理
- [ ] API 权限管理
- [ ] 日志记录
- [ ] 数据查询和分页

---

## 常见问题

### Q1: 连接错误 "password authentication failed"

**原因**: 用户名或密码错误

**解决方案**:
```bash
# 检查 PostgreSQL 用户配置
psql -U postgres -c "\du"

# 重置密码
psql -U postgres -c "ALTER USER fast_soy_user WITH PASSWORD 'new_password';"
```

### Q2: 连接错误 "database does not exist"

**原因**: 数据库未创建

**解决方案**:
```bash
psql -U postgres -c "CREATE DATABASE fast_soy_admin;"
```

### Q3: 迁移文件执行失败

**原因**: SQL 语法不兼容

**解决方案**:
1. 删除现有迁移文件
2. 重新生成迁移: `aerich init-db`
3. 手动检查并修复 SQL 语法

### Q4: 序列重置问题

**原因**: PostgreSQL 使用序列而非 SQLite 的 sqlite_sequence

**解决方案**:
```sql
-- 重置所有序列
SELECT setval(pg_get_serial_sequence('table_name', 'id'), 1, false);
```

### Q5: 时区问题

**原因**: PostgreSQL 对时区更严格

**解决方案**:
确保 `config.py` 中设置了正确的时区:
```python
"use_tz": False,
"timezone": "Asia/Shanghai"
```

---

## 迁移检查清单

### 代码修改
- [ ] 修改 `pyproject.toml` 依赖
- [ ] 修改 `app/settings/config.py` 连接配置
- [ ] 修改或重新生成迁移文件
- [ ] 修改 `cron_reset.py` 脚本
- [ ] 更新 `docker-compose.yml`（如使用）

### 环境配置
- [ ] 安装 PostgreSQL
- [ ] 创建数据库和用户
- [ ] 配置 `.env` 文件
- [ ] 安装新的 Python 依赖

### 测试验证
- [ ] 数据库连接测试
- [ ] 表结构验证
- [ ] 功能测试
- [ ] 性能测试

### 文档更新
- [ ] 更新 README.md
- [ ] 更新部署文档

---

## 回滚方案

如果迁移失败，可以回滚到 SQLite:

1. 恢复 `pyproject.toml` 依赖
2. 恢复 `app/settings/config.py` 配置
3. 恢复 SQLite 数据库文件（如果有备份）
4. 重新安装依赖: `pdm install`

---

## 总结

迁移到 PostgreSQL 的主要优势：
- ✅ 更好的并发性能
- ✅ 更强大的功能（JSON、全文搜索等）
- ✅ 更好的生产环境支持
- ✅ 更好的数据完整性保证

迁移完成后，记得：
1. 备份 PostgreSQL 数据库
2. 更新部署文档
3. 通知团队成员数据库变更

---

**文档版本**: 1.0  
**最后更新**: 2025-01-XX  
**维护者**: FastSoyAdmin Team

