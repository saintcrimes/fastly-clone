from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os
from sqlalchemy.orm import DeclarativeBase


path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(path)

db_url = os.getenv("DATABASE_URL")

engine = create_async_engine(
    db_url
)

session = async_sessionmaker(bind=engine, autocommit=False)

async def get_db():
    async with session() as ses:
        yield ses

class Base(DeclarativeBase):
    pass

