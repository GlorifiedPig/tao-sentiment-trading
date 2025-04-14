
# TODO: Staking logic.

# Imports
from typing import Optional, Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bittensor.core.settings import SS58_FORMAT
from async_substrate_interface import AsyncSubstrateInterface
from tao_redis import TaoRedis
from decouple import config
import asyncio
import uvicorn

# Configuration
example_hotkey: str = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
example_netuid: int = 18
default_username: str = "admin"
default_password: str = "admin"
example_token: str = "fake-token"
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
tao_redis_instance: TaoRedis = TaoRedis(host=redis_host, port=redis_port, db=redis_db)
substrate: AsyncSubstrateInterface = AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT)

async def get_total_networks() -> int:
    """Fetches the total number of networks from the blockchain.

    This also caches the value in Redis for 5 minutes, as this function is used a lot and querying it so often is not necessary.
    
    Returns:
        int: The total number of networks.
    """
    cached_total_networks = tao_redis_instance.get_total_networks()

    if cached_total_networks is not None:
        return cached_total_networks

    async with substrate:
        total_networks = (await substrate.query( module="SubtensorModule", storage_function="TotalNetworks" )).value
        tao_redis_instance.set_total_networks(total_networks)
        return total_networks

async def get_tao_dividends_per_subnet(netuid: int, hotkey: str) -> float:
    """Fetches dividends value from our specified netuid and hotkey.

    Args:
        netuid (int): The netuid to fetch the value for.
        hotkey (str): The hotkey to fetch the value for.

    Returns:
        float: The total dividend value for specified netuid and hotkey.
    """
    cached_dividends = tao_redis_instance.get_tao_dividends(netuid, hotkey)

    if cached_dividends is not None:
        return cached_dividends

    async with substrate:
        result = await substrate.query("SubtensorModule", "TaoDividendsPerSubnet", [netuid, hotkey])
        tao_redis_instance.set_tao_dividends(result.value, netuid, hotkey)
        return float(result.value)

async def get_tao_dividends_per_subnet_netuid(netuid: int) -> float:
    """Fetches total dividends from our specified netuid.

    Args:
        netuid (int): The netuid to fetch the value for.

    Returns:
        float: The total dividend value.
    """
    cached_dividends = tao_redis_instance.get_tao_dividends(netuid)

    if cached_dividends is not None:
        return cached_dividends

    async with substrate:
        block_hash = await substrate.get_chain_head()

        result = await substrate.query_map(
            module="SubtensorModule",
            storage_function="TaoDividendsPerSubnet",
            params=[netuid],
            block_hash=block_hash
        )

        total_dividends: float = 0
        async for _, v in result:
            total_dividends += v.value

        tao_redis_instance.set_tao_dividends(total_dividends, netuid)

        return float(total_dividends)

async def get_tao_dividends_per_subnet_all() -> float:
    """Fetches total dividends from all netuids.
    
    Args:
        None

    Returns:
        float: The total dividend value for all netuids.
    """
    async with substrate:
        block_hash = await substrate.get_chain_head()

        total_networks: int = await get_total_networks()

        tasks = [
            substrate.query_map(
            module="SubtensorModule",
            storage_function="TaoDividendsPerSubnet",
            params=[netuid],
                block_hash=block_hash
            ) for netuid in range(1, total_networks + 1)
        ]
        tasks = [exhaust(task) for task in tasks]

        total_dividends: float = 0

        for future in asyncio.as_completed(tasks):
            result = await future
            total_dividends += sum(v.value for _, v in result)

        return float(total_dividends)

# FastAPI
app = FastAPI(
    title="Tao Dividends API",
    description="An API to fetch Tao dividends from the blockchain.",
    contact={
        "name": "Ryan Cherry",
        "url": "https://github.com/GlorifiedPig",
        "email": "ryan@glorifiedstudios.com"
    },
    root_path="/api/v1"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token",
         tags=["auth"],
         summary="Login to the API.",
         response_description="Returns a JSON object with the login token.")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if form_data.username != default_username or form_data.password != default_password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return {
        "access_token": example_token,
        "token_type": "Bearer"
    }

@app.get("/tao_dividends",
         tags=["tao"],
         summary="Fetch Tao dividends.",
         response_description="Returns a JSON object with the dividends value.")
async def tao_dividends(token: Annotated[str, Depends(oauth2_scheme)], netuid: Optional[int] = None, hotkey: Optional[str] = None):
    if token != example_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    total_networks: int = await get_total_networks()

    if type(netuid) is int and (netuid < 1 or netuid > total_networks):
        raise HTTPException(status_code=400, detail="Invalid netuid")
    
    if type(hotkey) is str and netuid is None:
        raise HTTPException(status_code=400, detail="Hotkey provided but no netuid")
    
    cached: bool
    dividends: float

    cached_dividend = tao_redis_instance.get_tao_dividends(netuid, hotkey)

    if cached_dividend is not None:
        cached = True
        dividends = cached_dividend
    else:
        cached = False
        if netuid is not None and hotkey is not None:
            dividends = await get_tao_dividends_per_subnet(netuid, hotkey)
        elif netuid is not None:
            dividends = await get_tao_dividends_per_subnet_netuid(netuid)
        else:
            dividends = await get_tao_dividends_per_subnet_all()
        
        tao_redis_instance.set_tao_dividends(dividends, netuid, hotkey)

    return {
        "netuid": netuid,
        "hotkey": hotkey,
        "dividends": dividends,
        "cached": cached,
        "stake_tx_triggered": False # TODO
    }

@app.get("/total_networks",
         tags=["tao"],
         summary="Fetch the total number of networks.",
         response_description="Returns a JSON object with the total number of networks.")
async def total_networks(token: Annotated[str, Depends(oauth2_scheme)]):
    if token != example_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "total_networks": await get_total_networks()
    }

@app.get("/health",
         tags=["health"],
         summary="Check the health of the API.",
         response_description="Returns a 200 status code and a JSON object with the status 'ok'.")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)