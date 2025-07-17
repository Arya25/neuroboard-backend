from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from fastapi import Depends
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://neuroboard_db_user:wQZWqULzVp5R0VgdLkvwjAnTkYyTZ13r@dpg-d1s4d6mmcj7s73flvpl0-a.virginia-postgres.render.com/neuroboard_db"


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session