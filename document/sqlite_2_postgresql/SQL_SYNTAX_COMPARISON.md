# SQLite → PostgreSQL SQL 语法对比

本文档详细列出了迁移文件中需要修改的所有 SQL 语法差异。

## 📋 目录

1. [数据类型映射](#数据类型映射)
2. [自增主键](#自增主键)
3. [布尔类型](#布尔类型)
4. [注释语法](#注释语法)
5. [完整迁移文件示例](#完整迁移文件示例)

---

## 数据类型映射

| SQLite | PostgreSQL | 说明 |
|--------|------------|------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` | 自增主键 |
| `INT` | `INTEGER` | 整数（PostgreSQL 中 INT 是 INTEGER 的别名，但建议用 INTEGER） |
| `REAL` | `DOUBLE PRECISION` | 浮点数 |
| `INT DEFAULT 0` (布尔含义) | `BOOLEAN DEFAULT FALSE` | 布尔类型 |
| `VARCHAR(n)` | `VARCHAR(n)` | 字符串（相同） |
| `TIMESTAMP` | `TIMESTAMP` | 时间戳（相同） |
| `JSON` | `JSON` | JSON（相同） |

---

## 自增主键

### SQLite 语法
```sql
"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
```

### PostgreSQL 语法
```sql
"id" SERIAL PRIMARY KEY NOT NULL
```

### 注意事项
- PostgreSQL 中 `SERIAL` 会自动创建序列
- 也可以使用 `INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY`，但 `SERIAL` 更简洁

---

## 布尔类型

### SQLite 语法（使用 INT 0/1）
```sql
"multi_tab" INT NOT NULL DEFAULT 0
"keep_alive" INT NOT NULL DEFAULT 0
"hide_in_menu" INT NOT NULL DEFAULT 0
"props" INT NOT NULL DEFAULT 0
"constant" INT NOT NULL DEFAULT 0
```

### PostgreSQL 语法（使用 BOOLEAN）
```sql
"multi_tab" BOOLEAN NOT NULL DEFAULT FALSE
"keep_alive" BOOLEAN NOT NULL DEFAULT FALSE
"hide_in_menu" BOOLEAN NOT NULL DEFAULT FALSE
"props" BOOLEAN NOT NULL DEFAULT FALSE
"constant" BOOLEAN NOT NULL DEFAULT FALSE
```

### 字段识别
根据字段名和注释判断是否为布尔字段：
- `multi_tab` - 是否支持多页签
- `keep_alive` - 是否缓存
- `hide_in_menu` - 是否在菜单隐藏
- `props` - 是否为首路由
- `constant` - 是否为公共路由

---

## 注释语法

### SQLite 语法
```sql
"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 用户id */
```

### PostgreSQL 语法
```sql
"id" SERIAL PRIMARY KEY NOT NULL -- 用户id
```

### 批量替换规则
- `/* 注释 */` → `-- 注释`
- 注意：表注释 `) /* 表名 */;` 也需要改为 `) -- 表名;`

---

## 完整迁移文件示例

以下是修改后的完整迁移文件示例（关键部分）：

```python
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- API日志表
        CREATE TABLE IF NOT EXISTS "api_logs" (
            "id" SERIAL PRIMARY KEY NOT NULL, -- API日志id
            "x_request_id" VARCHAR(32) NOT NULL, -- 请求id
            "ip_address" VARCHAR(60), -- IP地址
            "user_agent" VARCHAR(500), -- User-Agent
            "request_domain" VARCHAR(200) NOT NULL, -- 请求域名
            "request_path" VARCHAR(500) NOT NULL, -- 请求路径
            "request_params" JSON, -- 请求参数
            "request_data" JSON, -- 请求体数据
            "response_data" JSON, -- 响应数据
            "response_code" VARCHAR(6), -- 业务状态码
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
            "process_time" DOUBLE PRECISION -- 请求处理时间
        ); -- API日志
        
        CREATE INDEX IF NOT EXISTS "idx_api_logs_create__a34f2a" ON "api_logs" ("create_time");
        CREATE INDEX IF NOT EXISTS "idx_api_logs_process_067c26" ON "api_logs" ("process_time");
        CREATE INDEX IF NOT EXISTS "idx_api_logs_x_reque_0dc622" ON "api_logs" ("x_request_id");
        CREATE INDEX IF NOT EXISTS "idx_api_logs_request_3eb14c" ON "api_logs" ("request_path");
        CREATE INDEX IF NOT EXISTS "idx_api_logs_respons_88b25b" ON "api_logs" ("response_code");
        
        -- API表
        CREATE TABLE IF NOT EXISTS "apis" (
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "update_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL PRIMARY KEY NOT NULL, -- API id
            "api_path" VARCHAR(500) NOT NULL, -- API路径
            "api_method" VARCHAR(6) NOT NULL, -- 请求方法
            "summary" VARCHAR(500), -- 请求简介
            "tags" JSON, -- API标签
            "status_type" VARCHAR(1) NOT NULL DEFAULT '1' -- 状态
        ); -- API表
        
        CREATE INDEX IF NOT EXISTS "idx_apis_api_pat_12f5ea" ON "apis" ("api_path");
        CREATE INDEX IF NOT EXISTS "idx_apis_api_met_5933fc" ON "apis" ("api_method");
        CREATE INDEX IF NOT EXISTS "idx_apis_summary_8f6762" ON "apis" ("summary");
        
        -- 按钮表
        CREATE TABLE IF NOT EXISTS "buttons" (
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "update_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL PRIMARY KEY NOT NULL, -- 按钮id
            "button_code" VARCHAR(200) NOT NULL, -- 按钮编码
            "button_desc" VARCHAR(200) NOT NULL, -- 按钮描述
            "status_type" VARCHAR(1) NOT NULL DEFAULT '1' -- 状态
        );
        
        -- 菜单表（重点：布尔字段）
        CREATE TABLE IF NOT EXISTS "menus" (
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "update_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL PRIMARY KEY NOT NULL, -- 菜单id
            "menu_name" VARCHAR(100) NOT NULL, -- 菜单名称
            "menu_type" VARCHAR(1) NOT NULL, -- 菜单类型
            "route_name" VARCHAR(100) NOT NULL UNIQUE, -- 路由名称
            "route_path" VARCHAR(200) NOT NULL UNIQUE, -- 路由路径
            "path_param" VARCHAR(200), -- 路径参数
            "route_param" JSON, -- 路由参数, List[dict]
            "order" INTEGER NOT NULL DEFAULT 0, -- 菜单顺序
            "component" VARCHAR(100), -- 路由组件
            "parent_id" INTEGER NOT NULL DEFAULT 0, -- 父菜单ID
            "i18n_key" VARCHAR(100), -- 用于国际化的展示文本，优先级高于title
            "icon" VARCHAR(100), -- 图标名称
            "icon_type" VARCHAR(1), -- 图标类型
            "href" VARCHAR(200), -- 外链
            "multi_tab" BOOLEAN NOT NULL DEFAULT FALSE, -- 是否支持多页签
            "keep_alive" BOOLEAN NOT NULL DEFAULT FALSE, -- 是否缓存
            "hide_in_menu" BOOLEAN NOT NULL DEFAULT FALSE, -- 是否在菜单隐藏
            "fixed_index_in_tab" INTEGER, -- 固定在页签的序号
            "status_type" VARCHAR(1) NOT NULL DEFAULT '1', -- 菜单状态
            "redirect" VARCHAR(200), -- 重定向路径
            "props" BOOLEAN NOT NULL DEFAULT FALSE, -- 是否为首路由
            "constant" BOOLEAN NOT NULL DEFAULT FALSE, -- 是否为公共路由
            "active_menu_id" INTEGER REFERENCES "menus" ("id") ON DELETE CASCADE -- 隐藏的路由需要激活的菜单
        ); -- 菜单表
        
        -- 角色表
        CREATE TABLE IF NOT EXISTS "roles" (
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "update_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL PRIMARY KEY NOT NULL, -- 角色id
            "role_name" VARCHAR(20) NOT NULL UNIQUE, -- 角色名称
            "role_code" VARCHAR(20) NOT NULL UNIQUE, -- 角色编码
            "role_desc" VARCHAR(500), -- 角色描述
            "status_type" VARCHAR(1) NOT NULL DEFAULT '1', -- 状态
            "by_role_home_id" INTEGER NOT NULL REFERENCES "menus" ("id") ON DELETE CASCADE -- 角色首页
        ); -- 角色表
        
        CREATE INDEX IF NOT EXISTS "idx_roles_role_na_e92d59" ON "roles" ("role_name");
        CREATE INDEX IF NOT EXISTS "idx_roles_role_co_f4cc69" ON "roles" ("role_code");
        CREATE INDEX IF NOT EXISTS "idx_roles_status__597955" ON "roles" ("status_type");
        
        -- 用户表
        CREATE TABLE IF NOT EXISTS "users" (
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "update_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL PRIMARY KEY NOT NULL, -- 用户id
            "user_name" VARCHAR(20) NOT NULL UNIQUE, -- 用户名称
            "password" VARCHAR(128) NOT NULL, -- 密码
            "nick_name" VARCHAR(30), -- 昵称
            "user_gender" VARCHAR(1) NOT NULL DEFAULT '3', -- 性别
            "user_email" VARCHAR(255) UNIQUE, -- 邮箱
            "user_phone" VARCHAR(20), -- 电话
            "last_login" TIMESTAMP, -- 最后登录时间
            "status_type" VARCHAR(1) NOT NULL DEFAULT '1' -- 状态
        ); -- 用户表
        
        CREATE INDEX IF NOT EXISTS "idx_users_user_na_7a1e93" ON "users" ("user_name");
        CREATE INDEX IF NOT EXISTS "idx_users_nick_na_7d3545" ON "users" ("nick_name");
        CREATE INDEX IF NOT EXISTS "idx_users_user_ge_fe41ac" ON "users" ("user_gender");
        CREATE INDEX IF NOT EXISTS "idx_users_user_em_d720cf" ON "users" ("user_email");
        CREATE INDEX IF NOT EXISTS "idx_users_user_ph_b2a4cb" ON "users" ("user_phone");
        CREATE INDEX IF NOT EXISTS "idx_users_status__098c93" ON "users" ("status_type");
        
        -- 日志表
        CREATE TABLE IF NOT EXISTS "logs" (
            "id" SERIAL PRIMARY KEY NOT NULL, -- 日志id
            "log_type" VARCHAR(1) NOT NULL, -- 日志类型
            "log_detail_type" VARCHAR(4), -- 日志详情类型
            "create_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
            "x_request_id" VARCHAR(32), -- 请求id
            "by_user_id" INTEGER REFERENCES "users" ("id") ON DELETE CASCADE, -- 关联专员
            "api_log_id" INTEGER UNIQUE REFERENCES "api_logs" ("id") ON DELETE SET NULL -- API日志
        ); -- 日志表
        
        CREATE INDEX IF NOT EXISTS "idx_logs_log_typ_88d44b" ON "logs" ("log_type");
        CREATE INDEX IF NOT EXISTS "idx_logs_by_user_5fc8d2" ON "logs" ("by_user_id");
        CREATE INDEX IF NOT EXISTS "idx_logs_log_det_a9ea91" ON "logs" ("log_detail_type");
        CREATE INDEX IF NOT EXISTS "idx_logs_x_reque_99e858" ON "logs" ("x_request_id");
        
        -- Aerich 迁移表
        CREATE TABLE IF NOT EXISTS "aerich" (
            "id" SERIAL PRIMARY KEY NOT NULL,
            "version" VARCHAR(255) NOT NULL,
            "app" VARCHAR(100) NOT NULL,
            "content" JSON NOT NULL
        );
        
        -- 关联表（多对多关系）
        CREATE TABLE IF NOT EXISTS "menus_buttons" (
            "menus_id" INTEGER NOT NULL REFERENCES "menus" ("id") ON DELETE CASCADE,
            "button_id" INTEGER NOT NULL REFERENCES "buttons" ("id") ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "uidx_menus_butto_menus_i_a9336b" ON "menus_buttons" ("menus_id", "button_id");
        
        CREATE TABLE IF NOT EXISTS "roles_apis" (
            "roles_id" INTEGER NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
            "api_id" INTEGER NOT NULL REFERENCES "apis" ("id") ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "uidx_roles_apis_roles_i_753aef" ON "roles_apis" ("roles_id", "api_id");
        
        CREATE TABLE IF NOT EXISTS "roles_menus" (
            "roles_id" INTEGER NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
            "menu_id" INTEGER NOT NULL REFERENCES "menus" ("id") ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "uidx_roles_menus_roles_i_3d4119" ON "roles_menus" ("roles_id", "menu_id");
        
        CREATE TABLE IF NOT EXISTS "roles_buttons" (
            "roles_id" INTEGER NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
            "button_id" INTEGER NOT NULL REFERENCES "buttons" ("id") ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "uidx_roles_butto_roles_i_f9441d" ON "roles_buttons" ("roles_id", "button_id");
        
        CREATE TABLE IF NOT EXISTS "users_roles" (
            "users_id" INTEGER NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
            "role_id" INTEGER NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "uidx_users_roles_users_i_baf5e4" ON "users_roles" ("users_id", "role_id");
    """
```

---

## 修改检查清单

### 必须修改的项

- [ ] `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY` (所有表)
- [ ] `REAL` → `DOUBLE PRECISION` (process_time 字段)
- [ ] `INT DEFAULT 0` (布尔字段) → `BOOLEAN DEFAULT FALSE` (5个字段)
- [ ] `/* 注释 */` → `-- 注释` (所有注释)

### 建议修改的项

- [ ] `INT` → `INTEGER` (更明确)
- [ ] 表注释格式统一

### 不需要修改的项

- ✅ `VARCHAR(n)` - 相同
- ✅ `TIMESTAMP` - 相同
- ✅ `JSON` - 相同
- ✅ `REFERENCES` - 相同
- ✅ `ON DELETE CASCADE` - 相同
- ✅ `CREATE INDEX` - 相同
- ✅ `UNIQUE` - 相同

---

## 批量替换脚本（参考）

如果需要批量替换，可以使用以下 sed 命令（**请先备份文件**）：

```bash
# 备份原文件
cp migrations/app_system/0_20251106095928_init.py migrations/app_system/0_20251106095928_init.py.backup

# 替换自增主键
sed -i '' 's/INTEGER PRIMARY KEY AUTOINCREMENT/SERIAL PRIMARY KEY/g' migrations/app_system/0_20251106095928_init.py

# 替换浮点数
sed -i '' 's/REAL/DOUBLE PRECISION/g' migrations/app_system/0_20251106095928_init.py

# 替换布尔字段（需要手动确认每个字段）
# multi_tab
sed -i '' 's/"multi_tab" INT NOT NULL  DEFAULT 0/"multi_tab" BOOLEAN NOT NULL DEFAULT FALSE/g' migrations/app_system/0_20251106095928_init.py
# keep_alive
sed -i '' 's/"keep_alive" INT NOT NULL  DEFAULT 0/"keep_alive" BOOLEAN NOT NULL DEFAULT FALSE/g' migrations/app_system/0_20251106095928_init.py
# hide_in_menu
sed -i '' 's/"hide_in_menu" INT NOT NULL  DEFAULT 0/"hide_in_menu" BOOLEAN NOT NULL DEFAULT FALSE/g' migrations/app_system/0_20251106095928_init.py
# props
sed -i '' 's/"props" INT NOT NULL  DEFAULT 0/"props" BOOLEAN NOT NULL DEFAULT FALSE/g' migrations/app_system/0_20251106095928_init.py
# constant
sed -i '' 's/"constant" INT NOT NULL  DEFAULT 0/"constant" BOOLEAN NOT NULL DEFAULT FALSE/g' migrations/app_system/0_20251106095928_init.py

# 替换注释（注意：这个替换可能不够精确，建议手动检查）
sed -i '' 's|/\* \([^)]*\) \*/|-- \1|g' migrations/app_system/0_20251106095928_init.py
```

**⚠️ 警告**: 使用脚本替换后，务必仔细检查每个修改，确保没有误替换。

---

## 总结

主要修改点：
1. ✅ 自增主键：`AUTOINCREMENT` → `SERIAL`
2. ✅ 浮点数：`REAL` → `DOUBLE PRECISION`
3. ✅ 布尔类型：`INT DEFAULT 0` → `BOOLEAN DEFAULT FALSE`
4. ✅ 注释：`/* */` → `--`
5. ✅ INT → INTEGER（建议）

建议：**重新生成迁移文件**，而不是手动修改，这样可以避免错误。

---

**相关文档**:
- [完整迁移指南](MIGRATION_SQLITE_TO_POSTGRESQL.md)
- [快速迁移指南](MIGRATION_QUICK_GUIDE.md)

