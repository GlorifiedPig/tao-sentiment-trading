
# Imports
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
import asyncio
import bittensor

# Logic
substrate = AsyncSubstrateInterface(
    url="https://rpc.tao.network",
    ss58_format=SS58_FORMAT,
    type_registry_preset="tao"
)

async def exhaust(qmr):
    r = []
    async for k, v in await qmr:
        r.append((k, v))
    return r

async def fetch_last_dividend():
    async with substrate:
        block_hash = await substrate.get_block_hash()
        tasks = [
            substrate.query_map(
                "SubtensorModule",
                "TaoDividendsPerSubnet",
                [netuid],
                block_hash=block_hash,
            ) for netuid in range(1, 51)
        ]
        tasks = [exhaust(task) for task in tasks]

        results_dicts_list = []
        for future in asyncio.as_completed(tasks):
            result = await future
            results_dicts_list.extend([(decode_account_id(k), v.value) for k, v in result])

        return results_dicts_list, block_hash

# Routes
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/dividend")
async def dividend(netuid: int | None = None, hotkey: str | None = None, trade: bool = False):
    return await fetch_last_dividend(netuid, hotkey, trade)