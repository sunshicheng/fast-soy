#!/usr/bin/env python3
"""
PostgreSQL 数据库初始化脚本
用于创建数据库、用户和表结构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.settings import APP_SETTINGS
from tortoise import Tortoise


async def init_database():
    """初始化 PostgreSQL 数据库"""
    print("=" * 60)
    print("开始初始化 PostgreSQL 数据库...")
    print("=" * 60)
    
    # 数据库配置信息
    db_config = APP_SETTINGS.TORTOISE_ORM["connections"]["conn_system"]["credentials"]
    print(f"\n数据库配置:")
    print(f"  主机: {db_config['host']}")
    print(f"  端口: {db_config['port']}")
    print(f"  数据库: {db_config['database']}")
    print(f"  用户: {db_config['user']}")
    
    try:
        # 初始化 Tortoise ORM
        print("\n正在连接数据库...")
        await Tortoise.init(
            config=APP_SETTINGS.TORTOISE_ORM,
        )
        
        # 生成数据库表结构
        print("正在生成数据库表结构...")
        await Tortoise.generate_schemas()
        
        print("\n✅ 数据库初始化成功！")
        print("\n已创建以下表:")
        
        # 查询所有表
        conn = Tortoise.get_connection("conn_system")
        table_count, tables = await conn.execute_query("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        for table in tables:
            print(f"  - {table['tablename']}")
        
        print(f"\n总共创建了 {len(tables)} 个表")
        
        await Tortoise.close_connections()
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        print("\n请检查:")
        print("  1. PostgreSQL 服务是否已启动")
        print("  2. 数据库和用户是否已创建")
        print("  3. 数据库连接配置是否正确")
        print("\n创建数据库和用户的 SQL 命令:")
        print(f"""
        psql -U postgres << EOF
        CREATE DATABASE {db_config['database']};
        CREATE USER {db_config['user']} WITH PASSWORD '{db_config['password']}';
        GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['user']};
        \\c {db_config['database']}
        GRANT ALL ON SCHEMA public TO {db_config['user']};
        EOF
        """)
        await Tortoise.close_connections()
        return False


if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)

