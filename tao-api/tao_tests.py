
# Imports
import tao_sentiments

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

        print("Sentiment analysis tests passed!")
    
    def run_all_tests(self):
        self.sentiment_analysis_tests()