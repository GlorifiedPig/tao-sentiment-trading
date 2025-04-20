
# Imports
from decouple import config
import requests
from typing import Optional
import logging

# Configuration
DATURA_API_KEY: str = config("DATURA_API_KEY")
CHUTES_API_KEY: str = config("CHUTES_API_KEY")

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logic
datura_api_url: str = "https://apis.datura.ai/twitter"
chutes_api_url: str = "https://llm.chutes.ai/v1/chat/completions"

datura_api_headers: dict = {
    "Authorization": str(DATURA_API_KEY),
    "Content-Type": "application/json"
}

chutes_api_headers: dict = {
    "Authorization": f"Bearer {str(CHUTES_API_KEY)}",
    "Content-Type": "application/json"
}

def search_recent_tweets(netuid: int, tweet_count: int = 20) -> dict | None:
    """Fetches recent tweets about the given netuid.
    
    Args:
        netuid (int): The netuid to search for.

    Returns:
        dict | None: The recent tweets, or None if the request fails.
    """
    params = {
        "query": f"Bittensor netuid {netuid}",
        "sort": "Top",
        "tweet_count": 10
    }

    response = requests.get(url=datura_api_url, headers=datura_api_headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Search recent tweets failed: {str(response.json())}")
        return None
    
def perform_sentiment_analysis(text: str) -> int | None:
    """Performs sentiment analysis on the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        int | None: The sentiment score, or None if the score is out of range or the request fails.
    """
    prompt = f"Return ONLY a sentiment score of -100 to 100 for the following text: {text}\nPlease make sure you ONLY return the sentiment score number (-100 to 100) and nothing else."

    params = {
        "model": "unsloth/Llama-3.2-3B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.6
    }

    try:
        response = requests.post(url=chutes_api_url, headers=chutes_api_headers, json=params)

        if response.status_code == 200:
            response_data = response.json()
            content: str = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            score: int = int(content.strip())

            if -100 <= score <= 100:
                logger.info(f"Sentiment analysis score: {score}")
                return score
            else:
                logger.error(f"Sentiment analysis score is out of range: {score}")
                return None
        else:
            logger.error(f"Sentiment analysis failed: {str(response.json())}")
            return None
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return None

def sentiment_analysis_on_recent_tweets(netuid: int) -> int | None:
    """Performs sentiment analysis on the recent tweets about the given netuid.
    
    Args:
        netuid (int): The netuid to search for.

    Returns:
        int | None: The sentiment score, or None if the score is out of range or the request fails.
    """
    recent_tweets = search_recent_tweets(netuid)

    if recent_tweets is None:
        return None

    recent_tweets_string: str = ""
    for tweet in recent_tweets:
        recent_tweets_string += f"{tweet}\n"

    sentiment_score: int = perform_sentiment_analysis(recent_tweets_string)

    return sentiment_score