
# Imports
from decouple import config
from bittensor import Wallet, Balance
from bittensor.core import async_subtensor
from bittensor.utils.balance import tao
import traceback
import logging

# Configuration
TESTNET_URL: str = "wss://test.finney.opentensor.ai:443"
WALLET_NAME: str = config("WALLET_NAME")
WALLET_HOTKEY: str = config("WALLET_HOTKEY")
WALLET_PATH: str = "/app/wallets/"

# Configure Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Logic
class TaoWallet:
    def __init__(self):
        self.wallet = Wallet(name=WALLET_NAME, path=WALLET_PATH, hotkey=WALLET_HOTKEY) # NOTE: Make sure coldkey is not password protected!
        self.async_subtensor = async_subtensor.AsyncSubtensor(network=TESTNET_URL)

    async def add_stake(self, netuid: int, amount: float) -> bool:
        try:
            subnet = await self.async_subtensor.subnet(netuid=netuid)

            hotkey: str = subnet.owner_hotkey

            block_hash = await self.async_subtensor.substrate.get_chain_head()

            amount_balance: Balance = tao(amount)
            logger.info(f"Subnet slippage for {netuid}: {subnet.slippage(amount_balance)}")

            wallet_balance = await self.async_subtensor.get_balance(self.wallet.coldkeypub.ss58_address)
            logger.info(f"Wallet balance: {wallet_balance}")

            existential_deposit = await self.async_subtensor.get_existential_deposit(block_hash=block_hash)
            logger.info(f"Existential deposit: {existential_deposit}")

            if amount_balance > wallet_balance - existential_deposit:
                logger.info(f"Not enough balance to stake {amount} on {netuid}")
                return False

            logger.info(f"Staking {amount} on {netuid} with hotkey {hotkey}")

            success: bool = await self.async_subtensor.add_stake(
                wallet=self.wallet,
                netuid=netuid,
                amount=amount_balance,
                hotkey_ss58=hotkey,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=True,
                allow_partial_stake=False
            )
            if success:
                logger.info(f"Successfully staked {amount} on netuid {netuid}")
            else:
                logger.info(f"Failed to stake {amount} on netuid {netuid}")
            return success
        except Exception as e:
            logger.error(f"Error adding stake: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def unstake(self, netuid: int, amount: float) -> bool:
        try:
            subnet = await self.async_subtensor.subnet(netuid=netuid)
            hotkey: str = subnet.owner_hotkey

            balance: Balance = tao(amount)

            staked_amount = await self.async_subtensor.get_stake(
                netuid=netuid,
                coldkey_ss58=self.wallet.coldkeypub.ss58_address,
                hotkey_ss58=hotkey
            )
            logger.info(f"Staked amount: {staked_amount}")

            if staked_amount < balance:
                logger.info(f"Not enough staked amount to unstake {amount} on {netuid}")
                return False
            
            logger.info(f"Unstaking {amount} on {netuid} with hotkey {hotkey}")

            success: bool = await self.async_subtensor.unstake(
                wallet=self.wallet,
                netuid=netuid,
                amount=balance,
                hotkey_ss58=hotkey,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                safe_staking=False,
                allow_partial_stake=False
            )
            if success:
                logger.info(f"Successfully unstaked {amount} on netuid {netuid}")
            else:
                logger.info(f"Failed to unstake {amount} on netuid {netuid}")
            return success
        except Exception as e:
            logger.error(f"Error unstaking: {e}")
            return False
    
    # async def test_stakes(self):
    #     await self.add_stake(netuid=0, amount=0.03)
    #     await self.unstake(netuid=0, amount=0.01)