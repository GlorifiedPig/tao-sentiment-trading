
# Imports
from decouple import config
from bittensor import Wallet, Balance
from bittensor.core import async_subtensor
from bittensor.utils.balance import check_and_convert_to_balance

# Configuration
TESTNET_URL: str = "wss://test.finney.opentensor.ai:443"
WALLET_NAME: str = config("WALLET_NAME")
WALLET_HOTKEY: str = config("WALLET_HOTKEY")
WALLET_PATH: str = "/app/wallets/"

# Logic
class TaoWallet:
    def __init__(self):
        self.wallet = Wallet(name=WALLET_NAME, path=WALLET_PATH, hotkey=WALLET_HOTKEY)
        print("Generating new coldkey...")
        self.wallet.create_new_coldkey(overwrite=True, use_password=False)
        self.async_subtensor = async_subtensor.AsyncSubtensor(network=TESTNET_URL)

    async def add_stake(self, netiud: int, amount: float) -> bool:
        try:
            balance: Balance = check_and_convert_to_balance(amount)
            success: bool = await self.async_subtensor.add_stake(
                wallet=self.wallet,
                netuid=netiud,
                amount=balance,
                hotkey_ss58=self.wallet.hotkey_str,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=False,
                allow_partial_stake=False
            )
            if success:
                print(f"Successfully staked {amount} on netuid {netiud}")
            else:
                print(f"Failed to stake {amount} on netuid {netiud}")
            return success
        except Exception as e:
            print(f"Error adding stake: {e}")
            return False
    
    async def unstake(self, netiud: int, amount: float) -> bool:
        try:
            balance: Balance = check_and_convert_to_balance(amount)
            success: bool = await self.async_subtensor.unstake(
                wallet=self.wallet,
                netuid=netiud,
                amount=balance,
                hotkey_ss58=self.wallet.hotkey_str,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=False,
                allow_partial_stake=False
            )
            if success:
                print(f"Successfully unstaked {amount} on netuid {netiud}")
            else:
                print(f"Failed to unstake {amount} on netuid {netiud}")
            return success
        except Exception as e:
            print(f"Error unstaking: {e}")
            return False
    
    async def test_stakes(self):
        await self.add_stake(netiud=0, amount=0.02)
        await self.unstake(netiud=0, amount=0.01)