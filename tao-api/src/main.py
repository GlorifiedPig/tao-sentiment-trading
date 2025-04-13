
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

# Logic
example_hotkey = "5FvFLiEWbDn5xdhjHt3M3E7ndjRYVr7ou8UjcvqhsMddxTJg"
example_netuid = 1

async def get_tao_dividends_per_subnet(netuid: int, hotkey: str) -> float:
    async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
        result = await substrate.query("SubtensorModule", "TaoDividendsPerSubnet", [netuid, hotkey])
        return result.value

# Routes
# TODO: Authentication
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

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