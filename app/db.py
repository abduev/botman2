import logging

from sqlalchemy import create_engine, text

from app.settings import DB_URL


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def execute_query(query: str):
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
        return result
    except Exception as e:
        logging.error(f"PostgreSQL Error: {e}")
        raise e
