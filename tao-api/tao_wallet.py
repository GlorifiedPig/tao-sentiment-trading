
# Imports
from decouple import config
from bittensor import Wallet, Balance
from bittensor.core import async_subtensor
from bittensor.utils.balance import tao
from bittensor.utils.btlogging import logging
import traceback

# Configuration
TESTNET_URL: str = "wss://test.finney.opentensor.ai:443"
WALLET_NAME: str = config("WALLET_NAME")
WALLET_HOTKEY: str = config("WALLET_HOTKEY")
WALLET_PATH: str = "/app/wallets/"

logging.setLevel("DEBUG")

# Logic
class TaoWallet:
    def __init__(self):
        self.wallet = Wallet(name=WALLET_NAME, path=WALLET_PATH, hotkey=WALLET_HOTKEY) # NOTE: Make sure coldkey is not password protected!
        print("Generating new coldkey...")
        self.async_subtensor = async_subtensor.AsyncSubtensor(network=TESTNET_URL)

    async def add_stake(self, netuid: int, amount: float) -> bool:
        try:
            subnet = await self.async_subtensor.subnet(netuid=netuid)

            block_hash = await self.async_subtensor.substrate.get_chain_head()

            amount_balance: Balance = tao(amount)
            print(f"Subnet slippage for {netuid}: {subnet.slippage(amount_balance)}")

            wallet_balance = await self.async_subtensor.get_balance(self.wallet.coldkeypub.ss58_address)
            print(f"Wallet balance: {wallet_balance}")

            existential_deposit = await self.async_subtensor.get_existential_deposit(block_hash=block_hash)
            print(f"Existential deposit: {existential_deposit}")

            if amount_balance > wallet_balance - existential_deposit:
                print(f"Not enough balance to stake {amount} on {netuid}")
                return False

            print(f"Staking {amount} on {netuid} with hotkey {subnet.owner_hotkey}")

            success: bool = await self.async_subtensor.add_stake(
                wallet=self.wallet,
                netuid=netuid,
                amount=amount_balance,
                hotkey_ss58=subnet.owner_hotkey,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=True,
                allow_partial_stake=False
            )
            if success:
                print(f"Successfully staked {amount} on netuid {netuid}")
            else:
                print(f"Failed to stake {amount} on netuid {netuid}")
            return success
        except Exception as e:
            print(f"Error adding stake: {e}")
            print(traceback.format_exc())
            return False
    
    async def unstake(self, netuid: int, amount: float) -> bool:
        try:
            balance: Balance = tao(amount)
            success: bool = await self.async_subtensor.unstake(
                wallet=self.wallet,
                netuid=netuid,
                amount=balance,
                hotkey_ss58=self.wallet.hotkey_str,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=False,
                allow_partial_stake=False
            )
            if success:
                print(f"Successfully unstaked {amount} on netuid {netuid}")
            else:
                print(f"Failed to unstake {amount} on netuid {netuid}")
            return success
        except Exception as e:
            print(f"Error unstaking: {e}")
            return False
    
    # async def test_stakes(self):
    #     await self.add_stake(netuid=0, amount=0.03)
    #     await self.unstake(netuid=0, amount=0.01)