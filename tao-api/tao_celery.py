
# Imports
from celery import Celery
from decouple import config
from tao_sentiments import TaoSentiments

# Configuration
CELERY_BROKER_URL: str = config("CELERY_BROKER_URL")

# Logic
celery = Celery(
    "tao_celery",
    broker=CELERY_BROKER_URL
)

@celery.task
def fetch_recent_tweets(tao_sentiments_instance: TaoSentiments, netuid: int) -> dict | None:
    return tao_sentiments_instance.fetch_recent_tweets(netuid)

@celery.task
def perform_sentiment_analysis(tao_sentiments_instance: TaoSentiments, text: str) -> int:
    return tao_sentiments_instance.perform_sentiment_analysis(text)

@celery.task
def sentiment_analysis_and_staking(tao_sentiments_instance: TaoSentiments, netuid: int, hotkey: str) -> int:
    pass

@celery.task
def test_task():
    print("Test task")