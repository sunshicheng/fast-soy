-- 创建 PostgreSQL 数据库和用户
-- 执行方式: psql -U postgres -f create_postgresql_db.sql

-- 创建数据库
CREATE DATABASE fast_admin;

-- 创建用户
CREATE USER fast_user WITH PASSWORD 'fast_admin_password';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE fast_admin TO fast_user;

-- 连接到新创建的数据库
\c fast_admin

-- 授予 schema 权限
GRANT ALL ON SCHEMA public TO fast_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fast_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fast_user;

-- 显示创建结果
\du
\l fast_admin

