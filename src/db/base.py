from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..mailsystem.config import Config

path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(path)

db_url = Config.DATABASE_URL

engine = create_async_engine(
    db_url
)

session = async_sessionmaker(bind=engine, autocommit=False)

async def get_db():
    async with session() as ses:
        yield ses

class Base(DeclarativeBase):
    pass

