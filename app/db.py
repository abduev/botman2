import logging

import asyncpg
from sqlalchemy import create_engine, text

from app.settings import DB_URL


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create this once at application startup
pool = None


async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(dsn=DB_URL, min_size=5, max_size=20)


async def close_db_pool():
    global pool
    if pool:
        await pool.close()


async def execute_query(query: str):
    if pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")

    try:
        async with pool.acquire() as conn:
            result = await conn.fetch(query)
        return result
    except Exception as e:
        logging.error(f"PostgreSQL Error: {e}")
        raise
# async def execute_query(query: str):
#     try:
#         engine = create_engine(DB_URL)
#         with engine.connect() as conn:
#             result = conn.execute(text(query)).fetchall()
#         return result
#     except Exception as e:
#         logging.error(f"PostgreSQL Error: {e}")
#         raise e


async def on_shutdown(application):
    global pool
    if pool:
        await pool.close()
