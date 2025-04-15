# Imports
from decouple import config
import requests

# Logic
class TaoSentiments:
    def __init__(self, datura_api_key: str, chutes_api_key: str):
        if datura_api_key is None:
            raise ValueError("DATURA_API_KEY is not set")

        self.datura_api_url: str = "https://apis.datura.ai/twitter"
        self.datura_api_headers = {
            "Authorization": str(datura_api_key),
            "Content-Type": "application/json"
        }

        self.chutes_api_url: str = "https://llm.chutes.ai/v1/chat/completions"
        self.chutes_api_headers = {
            "Authorization": f"Bearer {str(chutes_api_key)}",
            "Content-Type": "application/json"
        }

    def search_recent_tweets(self, netuid: int) -> dict | None:
        params = {
            "query": f"Bittensor netuid {netuid}",
            "sort": "Top",
            "count": 10
        }

        response = requests.get(url=self.datura_api_url, headers=self.datura_api_headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Search recent tweets failed: {str(response.json())}")
            return None
        
    def perform_sentiment_analysis(self, text: str) -> int | None:
        params = {
            "model": "unsloth/Llama-3.2-3B-Instruct",
            "messages": [{"role": "user", "content": "Give me a sentiment score of -100 to 100 for the following text, please only return the score and nothing else and make sure it is within the range of -100 to 100: " + text}],
            "stream": False
        }

        response = requests.post(url=self.chutes_api_url, headers=self.chutes_api_headers, json=params)

        if response.status_code == 200:
            try:
                response_data = response.json()
                # Extract the content from the response
                content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Try to convert the content to an integer
                score = int(''.join(c for c in content if c.isdigit() or c == '-'))

                print(score)
                # Validate the score is within range
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