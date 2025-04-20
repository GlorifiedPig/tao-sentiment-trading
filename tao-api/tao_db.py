# Imports
from decouple import config
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from datetime import datetime
import logging

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
    sentiment_score = Column(Float)
    stake_amount = Column(Float)

class TaoDB():
    def __init__(self) -> None:
        self.engine = create_engine(f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")
        Base.metadata.create_all(self.engine)
        self.session_handler = scoped_session(sessionmaker(bind=self.engine))