
# Imports
from celery import Celery
from decouple import config
from tao_wallet import TaoWallet
import tao_sentiments
import logging

# Configuration
CELERY_BROKER_URL: str = config("CELERY_BROKER_URL")

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logic
tao_wallet_instance: TaoWallet = TaoWallet()

celery_instance = Celery(
    "tao_celery",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BROKER_URL
)

@celery_instance.task
def search_recent_tweets(netuid: int) -> dict | None:
    return tao_sentiments.search_recent_tweets(netuid)

@celery_instance.task
def perform_sentiment_analysis(text: str) -> int:
    return tao_sentiments.perform_sentiment_analysis(text)

@celery_instance.task
def sentiment_analysis_on_recent_tweets(netuid: int) -> int | None:
    return tao_sentiments.sentiment_analysis_on_recent_tweets(netuid)

# TODO: Does hotkey need to be passed?
@celery_instance.task
def sentiment_analysis_and_staking(netuid: int = 18, hotkey: str = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v") -> bool:
    sentiment_score: int | None = tao_sentiments.sentiment_analysis_on_recent_tweets(netuid)

    if sentiment_score is None:
        logger.info("Sentiment score is None, not going to stake.")
        return False
    
    stake_amount: float = sentiment_score * 0.1

    if stake_amount == 0:
        logger.info("Stake amount is 0, not going to stake.")
        return False
    
    success: bool = False
    if stake_amount > 0:
        success: bool = tao_wallet_instance.add_stake(netuid, stake_amount)

        if success:
            logger.info(f"Successfully staked {stake_amount} on netuid {netuid}.")
        else:
            logger.info(f"Failed to stake {stake_amount} on netuid {netuid}.")
    elif stake_amount < 0:
        success: bool = tao_wallet_instance.unstake(netuid, stake_amount)

        if success:
            logger.info(f"Successfully unstaked {stake_amount} on netuid {netuid}.")
        else:
            logger.info(f"Failed to unstake {stake_amount} on netuid {netuid}.")

    return success

@celery_instance.task
def test_task():
    logger.info("Test task ran.")
    return True