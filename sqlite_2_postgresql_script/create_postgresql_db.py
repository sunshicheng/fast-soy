#!/usr/bin/env python3
"""
使用 Python 创建 PostgreSQL 数据库和用户
无需 psql 命令，直接使用 asyncpg 连接
"""
import asyncio
import sys
from pathlib import Path

try:
    import asyncpg
except ImportError:
    print("错误: 未安装 asyncpg")
    print("请运行: pip install asyncpg 或 pdm install")
    sys.exit(1)


async def create_database_and_user():
    """创建数据库和用户"""
    # 从配置文件读取配置
    try:
        from app.settings import APP_SETTINGS
        db_config = APP_SETTINGS.TORTOISE_ORM["connections"]["conn_system"]["credentials"]
        db_name = db_config["database"]
        db_user = db_config["user"]
        db_password = db_config["password"]
        db_host = db_config["host"]
        db_port = int(db_config["port"])
    except Exception as e:
        print(f"读取配置失败: {e}")
        print("使用默认配置...")
        # 使用与配置文件一致的默认值
        db_name = "fast_admin"
        db_user = "fast_user"
        db_password = "fast_admin_password"
        db_host = "localhost"
        db_port = 5432
    
    print("=" * 60)
    print("PostgreSQL 数据库创建脚本")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"  主机: {db_host}")
    print(f"  端口: {db_port}")
    print(f"  数据库: {db_name}")
    print(f"  用户: {db_user}")
    print(f"  密码: {'*' * len(db_password)}")
    print()
    
    try:
        # 连接到默认的 postgres 数据库来创建新数据库
        print("正在连接到 PostgreSQL 服务器...")
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user="postgres",  # 使用 postgres 超级用户
            database="postgres",  # 连接到默认数据库
            password=input("请输入 PostgreSQL postgres 用户的密码（如果需要）: ").strip() or None
        )
        
        print("✅ 连接成功！")
        
        # 检查用户是否存在
        print(f"\n检查用户 '{db_user}' 是否存在...")
        user_exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM pg_user WHERE usename = $1)
        """, db_user)
        
        if not user_exists:
            print(f"创建用户 '{db_user}'...")
            await conn.execute(f"""
                CREATE USER {db_user} WITH PASSWORD '{db_password}';
            """)
            print(f"✅ 用户 '{db_user}' 创建成功！")
        else:
            print(f"ℹ️  用户 '{db_user}' 已存在，跳过创建")
            # 更新密码
            try:
                await conn.execute(f"""
                    ALTER USER {db_user} WITH PASSWORD '{db_password}';
                """)
                print(f"✅ 已更新用户 '{db_user}' 的密码")
            except Exception as e:
                print(f"⚠️  更新密码失败（可能没有权限）: {e}")
        
        # 检查数据库是否存在
        print(f"\n检查数据库 '{db_name}' 是否存在...")
        db_exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)
        """, db_name)
        
        if not db_exists:
            print(f"创建数据库 '{db_name}'...")
            await conn.execute(f"""
                CREATE DATABASE {db_name};
            """)
            print(f"✅ 数据库 '{db_name}' 创建成功！")
        else:
            print(f"ℹ️  数据库 '{db_name}' 已存在，跳过创建")
        
        # 授予权限
        print(f"\n授予用户权限...")
        await conn.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};
        """)
        print(f"✅ 权限授予成功！")
        
        await conn.close()
        
        # 连接到新创建的数据库来设置 schema 权限
        print(f"\n设置 schema 权限...")
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user="postgres",
            database=db_name,
            password=input("再次输入 PostgreSQL postgres 用户的密码（如果需要）: ").strip() or None
        )
        
        await conn.execute(f"""
            GRANT ALL ON SCHEMA public TO {db_user};
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user};
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user};
        """)
        print(f"✅ Schema 权限设置成功！")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据库和用户创建完成！")
        print("=" * 60)
        print(f"\n数据库信息:")
        print(f"  数据库名: {db_name}")
        print(f"  用户名: {db_user}")
        print(f"  密码: {'*' * len(db_password)}")
        print(f"\n可以继续执行: python init_postgresql.py")
        return True
        
    except asyncpg.InvalidPasswordError:
        print("\n❌ 密码错误，请重试")
        return False
    except asyncpg.exceptions.InsufficientPrivilegeError as e:
        print(f"\n❌ 权限不足: {e}")
        print("\n请确保:")
        print("  1. 使用 postgres 超级用户运行此脚本")
        print("  2. 或者手动使用 psql 执行 create_postgresql_db.sql")
        return False
    except Exception as e:
        print(f"\n❌ 创建失败: {e}")
        print("\n可能的解决方案:")
        print("  1. 确保 PostgreSQL 服务正在运行")
        print("  2. 检查连接信息是否正确")
        print("  3. 如果不需要密码，可以尝试直接使用 psql")
        return False


if __name__ == "__main__":
    print("提示: 如果 PostgreSQL 不需要密码，直接按回车即可")
    success = asyncio.run(create_database_and_user())
    sys.exit(0 if success else 1)

