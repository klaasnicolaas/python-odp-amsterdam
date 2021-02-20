import aiohttp
import asyncio

import garages_amsterdam

async def main():
    """ Simple function to test the output. """
    async with aiohttp.ClientSession() as client:
        result = await garages_amsterdam.get_garages(client)
        print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())