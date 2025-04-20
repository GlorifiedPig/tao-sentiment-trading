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
MYSQL_USERNAME: str = config("MYSQL_USERNAME")
MYSQL_PASSWORD: str = config("MYSQL_PASSWORD")
MYSQL_DB: str = config("MYSQL_DB")

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logic
Base = declarative_base()

class TaoDB_Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)

class TaoDB_Sentiment(Base):
    __tablename__ = "sentiment"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    netuid = Column(Integer)
    hotkey = Column(String(255))
    sentiment = Column(Float)
    stake_amount = Column(Float)

class TaoDB():
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(f"mysql+asyncmy://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}")
        self.session_handler: async_scoped_session = async_scoped_session(async_sessionmaker(bind=self.engine), scopefunc=lambda: asyncio.current_task())