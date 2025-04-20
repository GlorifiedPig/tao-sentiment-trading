# Imports
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, async_sessionmaker, AsyncEngine
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import logging
import asyncio

# Configuration
MYSQL_HOST: str = config("MYSQL_HOST")
MYSQL_USER: str = config("MYSQL_USER")
MYSQL_PASSWORD: str = config("MYSQL_PASSWORD")
MYSQL_DATABASE: str = config("MYSQL_DATABASE")

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logic
Base = declarative_base()

class TaoDB_Dividend_Requests(Base):
    __tablename__ = "dividend_requests"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    netuid = Column(Integer, nullable=True, default=None)
    hotkey = Column(String(255), nullable=True, default=None)
    trade = Column(Boolean, default=False)

class TaoDB_Sentiment(Base):
    __tablename__ = "sentiment"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    netuid = Column(Integer)
    hotkey = Column(String(255))
    sentiment = Column(Float)
    stake_amount = Column(Float)

class TaoDB():
    async def create_engine(self):
        self.engine: AsyncEngine = create_async_engine(f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.session_handler: async_scoped_session = async_scoped_session(async_sessionmaker(bind=self.engine), scopefunc=lambda: asyncio.current_task())

    async def persist_dividend_request(self, netuid: int | None, hotkey: str | None, trade: bool):
        async with self.session_handler() as session:
            session.add(TaoDB_Dividend_Requests(
                timestamp=datetime.now(),
                netuid=netuid,
                hotkey=hotkey,
                trade=trade
            ))
            await session.commit()

    async def persist_sentiment(self, netuid: int, hotkey: str, sentiment: float, stake_amount: float):
        async with self.session_handler() as session:
            session.add(TaoDB_Sentiment(
                timestamp=datetime.now(),
                netuid=netuid,
                hotkey=hotkey,
                sentiment=sentiment,
                stake_amount=stake_amount
            ))
            await session.commit()