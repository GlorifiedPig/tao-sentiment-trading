# Imports
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
import asyncio
import time

# Logic
async def get_tao_dividends_per_subnet(netuid: int):
    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443",
                                       ss58_format=SS58_FORMAT) as substrate:
        block_hash = await substrate.get_chain_head()
        result = await substrate.query_map(
            module="SubtensorModule",
            storage_function="TaoDividendsPerSubnet",
            params=[netuid],
            block_hash=block_hash
        )
        
        results = []
        async for k, v in result:
            results.append((decode_account_id(k), v.value))
        return results

print(asyncio.run(get_tao_dividends_per_subnet(1)))

# Routes
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# TODO
@app.get("/api/v1/tao_dividends")
async def get_dividends():
    dividends = await get_tao_dividends_per_subnet()
    return {"tao_dividends_per_subnet": dividends}