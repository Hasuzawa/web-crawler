import asyncio
import os
from pathlib import Path

import aiohttp

from web_crawler import download, get_info


async def main():
    outdir = "download"
    try:
        os.mkdir(outdir)
    except:
        print(f"{outdir} directory exists")
    async with aiohttp.ClientSession() as session:
        async for name, url, skin in get_info(session):
            data = await download(session, url)
            name = name.replace(" ", "_")
            skin = skin.replace(" ", "_")
            filename = f"{name}_{skin}.png"
            # the name, skin pair is an unique pair so there is no need to worry about accidental overwrite
            path = Path(outdir, filename)
            path.write_bytes(data)


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(main())
