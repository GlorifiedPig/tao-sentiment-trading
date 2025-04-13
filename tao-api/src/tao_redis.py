
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
        """Fetches cached Tao Dividend values from Redis.
        
        Args:
            netuid (int | None): The netuid to fetch the value for, or None if all netuids.
            hotkey (str | None): The hotkey to fetch the value for, or None if all hotkeys.

        Returns:
            float | None: The total dividend value for specified netuid and hotkey, or None if no cached value.
        """
        netuid_part = str(netuid) if netuid is not None else "*"
        hotkey_part = hotkey if hotkey is not None else "*"
        key = f"tao_dividends:{netuid_part}:{hotkey_part}"

        dividend_value = self.redis.get(key)

        return float(dividend_value) if dividend_value is not None else None

    def set_tao_dividends(self, dividends: float, netuid: Optional[int] = None, hotkey: Optional[str] = None):
        """Updates cached Tao Dividend values in Redis.
        
        Args:
            dividends (float): The dividend value to update the cache with.
            netuid (int | None): The netuid to update the cache for, or None if all netuids.
            hotkey (str | None): The hotkey to update the cache for, or None if all hotkeys.
        """
        netuid_part = str(netuid) if netuid is not None else "*"
        hotkey_part = hotkey if hotkey is not None else "*"
        key = f"tao_dividends:{netuid_part}:{hotkey_part}"

        self.redis.set(key, dividends, ex=TAO_DIVIDEND_EXPIRY_SECONDS) # TODO: Is this expiry time in seconds?