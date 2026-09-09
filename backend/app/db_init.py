import asyncio
import os
import sys
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings
from app.core.neon_proxy import start_neon_proxy, stop_neon_proxy

SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql")

SQL_FILES = [
    "schema.sql",
    "seed.sql",
    "triggers_functions.sql",
    "views.sql",
    "finpulse_upgrade.sql",
    "local_auth_upgrade.sql"
]

async def run_sql_file(session, file_path):
    print(f"Executing {file_path}...")
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        sql = f.read()
        
    # Split by semicolon to execute one by one (basic approach)
    # Better: use the full block if the driver supports it
    try:
        await session.execute(text(sql))
        await session.commit()
        print(f"Successfully executed {file_path}")
        return True
    except Exception as e:
        await session.rollback()
        print(f"Error executing {file_path}: {e}")
        return False

async def init_db():
    if settings.is_neon_host and settings.neon_host:
        await start_neon_proxy(settings.neon_host, listen_port=5434)
    print(f"Initializing database using {settings.DATABASE_URL[:20]}...")
    try:
        # Use the SQLAlchemy engine to get a raw connection
        async with engine.connect() as conn:
        # The local Docker database persists between restarts. Avoid replaying
        # non-idempotent seed/DDL files once it has been initialized.
        existing = await conn.execute(text("SELECT to_regclass('public.app_users')"))
        if existing.scalar_one_or_none():
            print("Database already initialized; skipping DDL and seed files.")
            return
        files_to_run = ["local_auth_upgrade.sql"] if "--local-auth" in sys.argv else SQL_FILES
        for file_name in files_to_run:
            file_path = os.path.join(SQL_DIR, file_name)
            print(f"Executing {file_name}...")
            if not os.path.exists(file_path):
                print(f"Error: {file_path} not found.")
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                sql = f.read()
            
            try:
                # Use engine.raw_connection() to get access to the underlying driver
                # asyncpg supports multi-statement execution via its 'execute' method
                raw_conn = await conn.get_raw_connection()
                # Use the underlying asyncpg connection object
                await raw_conn.driver_connection.execute(sql)
                # The raw driver call participates in SQLAlchemy's connection
                # transaction; commit before the initializer container exits.
                await conn.commit()
                print(f"Successfully executed {file_name}")
            except Exception as e:
                print(f"Error executing {file_name}: {e}")
                sys.exit(1)
    finally:
        if settings.is_neon_host:
            await stop_neon_proxy()

if __name__ == "__main__":
    asyncio.run(init_db())
