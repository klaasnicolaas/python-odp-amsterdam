import aiohttp
import asyncio

import garages_amsterdam

async def main():
    """ Simple function to test the output. """
    async with aiohttp.ClientSession() as client:
        count = 0

        result = await garages_amsterdam.get_garages(client)
        for item in result:
            count+=1

        print(result)
        print(f'{count} parkeergarages gevonden')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())