# Imports
from fastapi import FastAPI
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
import asyncio
import time

# Logic
async def get_tao_dividends_per_subnet():
    async def exhaust(qmr):
        r = []
        async for k, v in await qmr:
            r.append((k, v))
        return r

    start = time.time()
    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443",
                                       ss58_format=SS58_FORMAT) as substrate:
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
        print(time.time() - start)
        results_dicts_list = []
        for future in asyncio.as_completed(tasks):
            result = await future
            results_dicts_list.extend([(decode_account_id(k), v.value) for k, v in result])

    elapsed = time.time() - start
    print(f"time elapsed: {elapsed}")

    print("Async Results", len(results_dicts_list))
    return results_dicts_list, block_hash

#print(asyncio.run(get_tao_dividends_per_subnet()))

async def get_tao_dividends_for_subnet(netuid: int):
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

print(asyncio.run(get_tao_dividends_for_subnet(1)))

# Routes
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/v1/tao_dividends")
async def get_dividends():
    dividends = await get_tao_dividends_per_subnet()
    return {"tao_dividends_per_subnet": dividends}