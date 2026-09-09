from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

connect_args = {}
if settings.is_neon_host:
    connect_args["ssl"] = False

engine = create_async_engine(
    settings.effective_db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=60,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
