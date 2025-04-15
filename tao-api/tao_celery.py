
# Imports
from celery import Celery
from decouple import config
import tao_sentiments

# Configuration
CELERY_BROKER_URL: str = config("CELERY_BROKER_URL")

# Logic
celery = Celery(
    "tao_celery",
    broker=CELERY_BROKER_URL
)

@celery.task
def search_recent_tweets(netuid: int) -> dict | None:
    return tao_sentiments.search_recent_tweets(netuid)

@celery.task
def perform_sentiment_analysis(text: str) -> int:
    return tao_sentiments.perform_sentiment_analysis(text)

@celery.task
def sentiment_analysis_on_recent_tweets(netuid: int) -> int:
    return tao_sentiments.sentiment_analysis_on_recent_tweets(netuid)

@celery.task
def sentiment_analysis_and_staking(netuid: int, hotkey: str) -> int:
    pass

@celery.task
def test_task():
    print("Test task")