import asyncio
from http import HTTPStatus
from typing import AsyncGenerator

import aiohttp
from bs4 import BeautifulSoup, ResultSet


async def get_info(
    session: aiohttp.ClientSession, /, cooldown: float = 0.1
) -> AsyncGenerator[tuple[str, str, str], None]:
    """generate info for downloading character image. Cooldown should be added between each request to not exhaust server resource of website."""

    async for character_name in gen_character_names(session):
        async for url, skin in gen_character_images(session, character_name):
            yield character_name, url, skin
            await asyncio.sleep(cooldown)
        await asyncio.sleep(cooldown)


async def gen_character_names(
    session: aiohttp.ClientSession,
) -> AsyncGenerator[str, None]:
    """generate names of all characters"""
    url = "https://azurlane.koumakan.jp/wiki/List_of_Ships_by_Image"

    async with session.get(url) as response:
        assert response.status == HTTPStatus.OK
        html = await response.text()
        dom = BeautifulSoup(html, features="html.parser")
        for card in dom.find_all("div", {"class": "azl-shipcard"}):
            anchor: ResultSet[any] = card.find("div", {"class": "alc-img"}).span.a
            character_name: str = anchor["title"]
            yield character_name


async def gen_character_images(
    session: aiohttp.ClientSession, character_name: str
) -> AsyncGenerator[tuple[str, str], None]:
    """generate url to character image and the name of the skin"""
    url = f"https://azurlane.koumakan.jp/wiki/{character_name}/Gallery"

    async with session.get(url) as response:
        assert response.status == HTTPStatus.OK
        html = await response.text()
        dom = BeautifulSoup(html, features="html.parser")
        for article in dom.find_all("article"):
            skin: str = article["data-title"]
            img: str = article.find("div", {"class": "shipskin-image"}).find("img")
            srcset: str = img["srcset"]
            last = srcset.split(",")[-1]
            link: str = last.strip()
            idx = link.rfind(".png")
            link = link[: idx + 4]
            print(link)
            yield link, skin


async def download(session: aiohttp.ClientSession, url: str) -> bytes:
    """return the content of the url"""
    async with session.get(url) as response:
        assert response.status == HTTPStatus.OK
        return await response.content.read()
