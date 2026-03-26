import aiohttp


aiohttp_client: aiohttp.ClientSession | None = None

async def init_aiohttp_client():
    global aiohttp_client
    aiohttp_client = aiohttp.ClientSession()

async def close_aiohttp_client():
    global aiohttp_client
    if aiohttp_client:
        await aiohttp_client.close()

def get_aiohttp_client() -> aiohttp.ClientSession:
    global aiohttp_client
    if aiohttp_client is None:
        raise RuntimeError("AsyncClient not initialized")
    return aiohttp_client
