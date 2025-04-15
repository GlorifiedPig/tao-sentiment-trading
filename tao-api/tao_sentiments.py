
# Imports
from decouple import config
import requests

# Configuration
DATURA_API_KEY: str = config("DATURA_API_KEY")
CHUTES_API_KEY: str = config("CHUTES_API_KEY")

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

def search_recent_tweets(netuid: int) -> dict | None:
    """Fetches recent tweets about the given netuid.
    
    Args:
        netuid (int): The netuid to search for.

    Returns:
        dict | None: The recent tweets, or None if the request fails.
    """
    params = {
        "query": f"Bittensor netuid {netuid}",
        "sort": "Top",
        "count": 10
    }

    response = requests.get(url=datura_api_url, headers=datura_api_headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Search recent tweets failed: {str(response.json())}")
        return None
    
def perform_sentiment_analysis(text: str) -> int | None:
    """Performs sentiment analysis on the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        int | None: The sentiment score, or None if the score is out of range or the request fails.
    """
    params = {
        "model": "unsloth/Llama-3.2-3B-Instruct",
        "messages": [{"role": "user", "content": "Give me a sentiment score of -100 to 100 for the following text, please only return the score and nothing else and make sure it is within the range of -100 to 100: " + text}],
        "stream": False
    }

    response = requests.post(url=chutes_api_url, headers=chutes_api_headers, json=params)

    if response.status_code == 200:
        try:
            response_data = response.json()
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            score = int(''.join(c for c in content if c.isdigit() or c == '-'))

            if -100 <= score <= 100:
                return score
            else:
                print(f"Sentiment score out of range: {score}")
                return None
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error parsing sentiment score: {e}")
            return None
    else:
        print(f"Sentiment analysis failed: {str(response.text)}")
        return None