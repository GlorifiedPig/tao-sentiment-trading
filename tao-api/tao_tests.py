
# Imports
from tao_celery import celery_instance, test_task
import tao_sentiments
import time
import logging

# Configure Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Logic
class TaoTests:
    def __init__(self):
        pass

    def sentiment_analysis_tests(self):
        positive_score: int | None = tao_sentiments.perform_sentiment_analysis("I am extremely happy about this and I think it is a great thing!")

        assert positive_score is not None
        assert positive_score > 0

        negative_score: int | None = tao_sentiments.perform_sentiment_analysis("This is absolutely terrible and I hate it!")

        assert negative_score is not None
        assert negative_score < 0

        logger.info("Sentiment analysis tests passed!")
    
    def fetch_recent_tweets_tests(self):
        recent_tweets: dict | None = tao_sentiments.search_recent_tweets(netuid=0)

        assert recent_tweets is not None
        assert len(recent_tweets) > 0

        logger.info("Fetch recent tweets tests passed!")
    
    def can_send_task_to_celery(self):
        logger.info("Sending task to celery...")
        result = test_task.delay()
    
    def run_all_tests(self):
        self.sentiment_analysis_tests()
        self.fetch_recent_tweets_tests()
        self.can_send_task_to_celery()