
# Imports
from decouple import config
from bittensor import Wallet
from bittensor.core import async_subtensor

# Configuration
TESTNET_URL: str = "https://test.chain.opentensor.ai"
WALLET_NAME: str = config("WALLET_NAME")
WALLET_PATH: str = config("WALLET_PATH")
WALLET_HOTKEY: str = config("WALLET_HOTKEY")

# Logic
class TaoWallet:
    def __init__(self):
        self.wallet = Wallet(name=WALLET_NAME, path=WALLET_PATH, hotkey=WALLET_HOTKEY)
        self.async_subtensor = async_subtensor.AsyncSubtensor(network=TESTNET_URL)

    async def add_stake(self, netiud: int, amount: float) -> bool:
        return await self.async_subtensor.add_stake(
            wallet=self.wallet,
            netuid=netiud,
            amount=amount
        )
    
    async def unstake(self, netiud: int, amount: float) -> bool:
        return await self.async_subtensor.unstake(
            wallet=self.wallet,
            netuid=netiud,
            amount=amount
        )
    
    async def test_stakes(self):
        await self.add_stake(netiud=1, amount=0.01)
        await self.unstake(netiud=1, amount=0.01)