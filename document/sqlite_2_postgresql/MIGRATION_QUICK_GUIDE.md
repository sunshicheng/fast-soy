# SQLite → PostgreSQL 快速迁移指南

## 🚀 快速开始

### 1. 安装 PostgreSQL 驱动

```bash
# 使用 PDM
pdm remove tortoise-orm[aiosqlite]
pdm add "tortoise-orm[asyncpg]>=0.20.1"

# 或使用 pip
pip uninstall aiosqlite
pip install asyncpg
pip install "tortoise-orm[asyncpg]>=0.20.1"
```

### 2. 修改配置文件

**文件**: `app/settings/config.py`

```python
def tortoise_orm_factory() -> dict[str, Any]:
    return {
        "connections": {
            "conn_system": {
                "engine": "tortoise.backends.asyncpg",  # 修改这里
                "credentials": {
                    "host": "localhost",
                    "port": "5432",
                    "user": "fast_soy_user",
                    "password": "your_password",
                    "database": "fast_soy_admin",
                }
            }
        },
        # ... 其他配置保持不变
    }
```

### 3. 创建 PostgreSQL 数据库

```bash
psql -U postgres << EOF
CREATE DATABASE fast_soy_admin;
CREATE USER fast_soy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fast_soy_admin TO fast_soy_user;
EOF
```

### 4. 重新生成迁移文件

```bash
# 删除旧迁移
rm -rf migrations/app_system/0_*.py

# 重新初始化（会生成 PostgreSQL 兼容的迁移文件）
aerich init-db
```

### 5. 修改 cron_reset.py

**关键修改**:
```python
# 修改前 (SQLite)
table_count, tables = await conn.execute_query(
    'SELECT name FROM sqlite_master WHERE type = "table";'
)
await conn.execute_query(f'update sqlite_sequence SET seq = 0 where name = "{table_name}";')

# 修改后 (PostgreSQL)
table_count, tables = await conn.execute_query("""
    SELECT tablename FROM pg_tables 
    WHERE schemaname = 'public' AND tablename != 'aerich';
""")
await conn.execute_query(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
```

---

## 📝 文件修改清单

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `pyproject.toml` | 依赖包: `aiosqlite` → `asyncpg` | ⭐⭐⭐ 必须 |
| `app/settings/config.py` | 数据库连接配置 | ⭐⭐⭐ 必须 |
| `migrations/app_system/0_*.py` | SQL 语法转换 | ⭐⭐⭐ 必须 |
| `cron_reset.py` | 表查询和序列重置 | ⭐⭐ 重要 |
| `docker-compose.yml` | 添加 PostgreSQL 服务 | ⭐ 可选 |

---

## 🔍 SQL 语法对比

### 主要差异

| SQLite | PostgreSQL |
|--------|------------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| `REAL` | `DOUBLE PRECISION` |
| `INT DEFAULT 0` (布尔) | `BOOLEAN DEFAULT FALSE` |
| `sqlite_master` | `pg_tables` |
| `sqlite_sequence` | PostgreSQL 序列 |

### 完整示例

**修改前 (SQLite)**:
```sql
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "multi_tab" INT NOT NULL DEFAULT 0,
    "process_time" REAL
);
```

**修改后 (PostgreSQL)**:
```sql
CREATE TABLE "users" (
    "id" SERIAL PRIMARY KEY NOT NULL,
    "multi_tab" BOOLEAN NOT NULL DEFAULT FALSE,
    "process_time" DOUBLE PRECISION
);
```

---

## ⚠️ 注意事项

1. **布尔字段**: SQLite 使用 `INT 0/1`，PostgreSQL 使用 `BOOLEAN`
2. **自增 ID**: SQLite 用 `AUTOINCREMENT`，PostgreSQL 用 `SERIAL` 或序列
3. **浮点数**: SQLite 用 `REAL`，PostgreSQL 用 `DOUBLE PRECISION`
4. **序列重置**: PostgreSQL 使用 `RESTART IDENTITY` 而不是 `sqlite_sequence`

---

## 🧪 验证步骤

```bash
# 1. 测试连接
python -c "from app.settings import APP_SETTINGS; from tortoise import Tortoise; import asyncio; asyncio.run(Tortoise.init(config=APP_SETTINGS.TORTOISE_ORM))"

# 2. 检查表
psql -U fast_soy_user -d fast_soy_admin -c "\dt"

# 3. 启动应用
pdm run run.py
```

---

## 📚 详细文档

完整迁移指南请参考: `MIGRATION_SQLITE_TO_POSTGRESQL.md`

