# Imports
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
import asyncio
import time

# Logic
example_hotkey = "5FvFLiEWbDn5xdhjHt3M3E7ndjRYVr7ou8UjcvqhsMddxTJg"
example_netuid = 1

async def get_tao_dividends_per_subnet(netuid: int, hotkey: str):
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
            decoded_key = decode_account_id(k)
            if decoded_key == hotkey:
                results.append((decoded_key, v.value)) # TODO: Check if there is a way we can query the hotkey directly instead of filtering it in the for loop.

        return results

print(asyncio.run(get_tao_dividends_per_subnet(example_netuid, example_hotkey)))

# Routes
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/v1/tao_dividends/{netuid}/{hotkey}")
async def get_dividends(netuid: int, hotkey: str):
    dividends = await get_tao_dividends_per_subnet(netuid, hotkey)
    return {"tao_dividends": dividends}