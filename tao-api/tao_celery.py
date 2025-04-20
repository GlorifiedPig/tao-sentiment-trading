
# Imports
from celery import Celery
from decouple import config
from tao_wallet import TaoWallet
import tao_sentiments

# Configuration
CELERY_BROKER_URL: str = config("CELERY_BROKER_URL")

# Logic
tao_wallet_instance: TaoWallet = TaoWallet()

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
def sentiment_analysis_on_recent_tweets(netuid: int) -> int | None:
    return tao_sentiments.sentiment_analysis_on_recent_tweets(netuid)

# TODO: Does hotkey need to be passed?
@celery.task
def sentiment_analysis_and_staking(netuid: int = 18, hotkey: str = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v") -> bool:
    sentiment_score: int | None = tao_sentiments.sentiment_analysis_on_recent_tweets(netuid)

    if sentiment_score is None:
        print("Sentiment score is None, not going to stake.")
        return False
    
    stake_amount: float = sentiment_score * 0.1

    if stake_amount == 0:
        print("Stake amount is 0, not going to stake.")
        return False
    
    success: bool = False
    if stake_amount > 0:
        success: bool = tao_wallet_instance.add_stake(netuid, stake_amount)

        if success:
            print(f"Successfully staked {stake_amount} on netuid {netuid}.")
        else:
            print(f"Failed to stake {stake_amount} on netuid {netuid}.")
    elif stake_amount < 0:
        success: bool = tao_wallet_instance.unstake(netuid, stake_amount)

        if success:
            print(f"Successfully unstaked {stake_amount} on netuid {netuid}.")
        else:
            print(f"Failed to unstake {stake_amount} on netuid {netuid}.")

    return success

@celery.task
def test_task():
    print("Test task")