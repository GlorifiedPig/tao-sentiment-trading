
# TODO: Caching layer.
# TODO: Staking logic.

# Imports
from typing import Optional
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
from tao_redis import TaoRedis
from decouple import config
import asyncio
import uvicorn
import time

# Configuration
example_hotkey: str = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
example_netuid: int = 18
redis_host: str = config("REDIS_HOST", default="localhost")
redis_port: int = config("REDIS_PORT", default=6379)
redis_db: int = config("REDIS_DB", default=0)

# Utils
async def exhaust(qmr):
    r = []
    async for k, v in await qmr:
        r.append((k, v))
    return r

# Logic
tao_redis_instance = TaoRedis(host=redis_host, port=redis_port, db=redis_db)

async def get_tao_dividends_per_subnet(netuid: int, hotkey: str) -> float:
    """Fetches TaoDividendsPerSubnet value with our specified netuid and hotkey.
    
    First checks if we have any cached value from Redis (which is stored by default for 2 minutes)

    If not, we query and update the Redis cache.
    
    Args:
        netuid (int): The netuid to fetch the value for.
        hotkey (str): The hotkey to fetch the value for.

    Returns:
        float: The total dividend value for specified netuid and hotkey.
    """
    cached_dividends = tao_redis_instance.get_tao_dividends(netuid, hotkey)

    if cached_dividends is not None:
        return cached_dividends

    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
        result = await substrate.query("SubtensorModule", "TaoDividendsPerSubnet", [netuid, hotkey])
        tao_redis_instance.set_tao_dividends(result.value, netuid, hotkey)
        return float(result.value)

async def get_tao_dividends_per_subnet_netuid(netuid: int) -> float:
    """Fetches TaoDividendsPerSubnet value with our specified netuid.
    
    First checks if we have any cached value from Redis (which is stored by default for 2 minutes)

    If not, we query and update the Redis cache.
    
    Args:
        netuid (int): The netuid to fetch the value for.

    Returns:
        float: The total dividend value.
    """
    cached_dividends = tao_redis_instance.get_tao_dividends(netuid)

    if cached_dividends is not None:
        return cached_dividends

    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443",
                                       ss58_format=SS58_FORMAT) as substrate:
        block_hash = await substrate.get_chain_head()

        result = await substrate.query_map(
            module="SubtensorModule",
            storage_function="TaoDividendsPerSubnet",
            params=[netuid],
            block_hash=block_hash
        )
        
        total_dividends: float = 0

        async for k, v in result:
            total_dividends += v.value # TODO Is this the right way to be fetching the totals?

        tao_redis_instance.set_tao_dividends(total_dividends, netuid)

        return float(total_dividends)

async def get_tao_dividends_per_subnet_all() -> float:
    """Fetches TaoDividendsPerSubnet value with all netuids.
    
    First checks if we have any cached value from Redis (which is stored by default for 2 minutes)

    If not, we query and update the Redis cache.
    
    Args:
        None

    Returns:
        float: The total dividend value for all netuids.
    """
    cached_dividends = tao_redis_instance.get_tao_dividends()

    if cached_dividends is not None:
        return cached_dividends

    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
        block_hash = await substrate.get_chain_head()

        tasks = [
            substrate.query_map(
            module="SubtensorModule",
            storage_function="TaoDividendsPerSubnet",
            params=[netuid],
                block_hash=block_hash
            ) for netuid in range(1, 51)
        ]
        tasks = [exhaust(task) for task in tasks]

        total_dividends: float = 0

        for future in asyncio.as_completed(tasks):
            result = await future
            for k, v in result:
                total_dividends += v.value # TODO Is this the right way to be fetching the totals?

        tao_redis_instance.set_tao_dividends(total_dividends)

        return float(total_dividends)

# Routes
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# TODO: Move caching logic to the routes / API section instead of the backend.
@app.get("/api/v1/tao_dividends")
async def tao_dividends(netuid: Optional[int] = None, hotkey: Optional[str] = None):
    if netuid is not None and hotkey is not None:
        dividends = await get_tao_dividends_per_subnet(netuid, hotkey)
    elif netuid is not None:
        dividends = await get_tao_dividends_per_subnet_netuid(netuid)
    else:
        dividends = await get_tao_dividends_per_subnet_all()
    
    # TODO: Error handling.
    # TODO: Invalid netuid / hotkey handling.
    # TODO: Authentication.

    return {
        "netuid": netuid,
        "hotkey": hotkey,
        "dividends": dividends,
        "cached": False, # TODO,
        "stake_tx_triggered": False # TODO
    }

@app.get("/health")
async def health():
    """This route always returns a 200 status code and a JSON object with the status "ok"."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)