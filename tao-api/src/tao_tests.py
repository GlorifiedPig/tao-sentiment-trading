
# Imports
from tao_sentiments import TaoSentiments

# Logic
class TaoTests:
    def __init__(self, tao_sentiments_instance: TaoSentiments):
        self.tao_sentiments_instance = tao_sentiments_instance

    def sentiment_analysis_tests(self):
        positive_score: int | None = self.tao_sentiments_instance.perform_sentiment_analysis("I am extremely happy about this and I think it is a great thing!")

        assert positive_score is not None
        assert positive_score > 0

        negative_score: int | None = self.tao_sentiments_instance.perform_sentiment_analysis("This is absolutely terrible and I hate it!")

        assert negative_score is not None
        assert negative_score < 0

        neutral_score: int | None = self.tao_sentiments_instance.perform_sentiment_analysis("I am neutral about this.")
        assert neutral_score is not None
        assert neutral_score > -20 and neutral_score < 20

        print("Sentiment analysis tests passed!")
    
    def run_all_tests(self):
        self.sentiment_analysis_tests()