
# Imports
import redis
from typing import Optional

# Configuration
TAO_DIVIDEND_EXPIRY_SECONDS = 120

# Logic
class TaoRedis:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self.redis = redis.Redis(host=host, port=port, db=db)

    def get_tao_dividends(self, netuid: Optional[int] = None, hotkey: Optional[str] = None) -> float | None:
        dividend_value = None

        if netuid is not None and hotkey is not None:
            dividend_value = self.redis.get(f"tao_dividends:{netuid}:{hotkey}")
        elif netuid is not None:
            dividend_value = self.redis.get(f"tao_dividends:{netuid}:*")
        else:
            dividend_value = self.redis.get("tao_dividends:*:*")

        if dividend_value is not None:
            return float(dividend_value)
        else:
            return None

    def set_tao_dividends(self, dividends: float, netuid: Optional[int] = None, hotkey: Optional[str] = None) -> None:
        if netuid is not None and hotkey is not None:
            self.redis.set(f"tao_dividends:{netuid}:{hotkey}", dividends, ex=TAO_DIVIDEND_EXPIRY_SECONDS)
        elif netuid is not None:
            self.redis.set(f"tao_dividends:{netuid}:*", dividends, ex=TAO_DIVIDEND_EXPIRY_SECONDS)
        elif hotkey is not None:
            self.redis.set(f"tao_dividends:*:{hotkey}", dividends, ex=TAO_DIVIDEND_EXPIRY_SECONDS)
            