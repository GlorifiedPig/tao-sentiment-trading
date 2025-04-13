
# TODO: Caching layer.
# TODO: Staking logic.

# Imports
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
import asyncio
import uvicorn
import time

# Utils
async def exhaust(qmr):
    r = []
    async for k, v in await qmr:
        r.append((k, v))
    return r

# Logic
example_hotkey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
example_netuid = 18

async def get_tao_dividends_per_subnet(netuid: int, hotkey: str) -> float:
    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
        result = await substrate.query("SubtensorModule", "TaoDividendsPerSubnet", [netuid, hotkey])
        return result.value

async def get_tao_dividends_per_subnet_netuid(netuid: int) -> float:
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
            total_dividends += v.value

        return total_dividends

async def get_tao_dividends_per_subnet_all() -> float:
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
                total_dividends += v.value

        return total_dividends

# Routes
# TODO: Authentication
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/v1/tao_dividends")
async def get_all_dividends():
    dividends = await get_tao_dividends_per_subnet_all()
    return {
        "dividends": dividends,
        "cached": False, # TODO,
        "stake_tx_triggered": False # TODO
    }


@app.get("/api/v1/tao_dividends/{netuid}")
async def get_dividends(netuid: int):
    dividends = await get_tao_dividends_per_subnet_netuid(netuid)
    return {
        "netuid": netuid,
        "dividend": dividends,
        "cached": False, # TODO,
        "stake_tx_triggered": False # TODO
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/api/v1/tao_dividends/{netuid}/{hotkey}")
async def get_dividends(netuid: int, hotkey: str):
    dividends = await get_tao_dividends_per_subnet(netuid, hotkey)
    return {
        "netuid": netuid,
        "hotkey": hotkey,
        "dividend": dividends,
        "cached": False, # TODO,
        "stake_tx_triggered": False # TODO
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)