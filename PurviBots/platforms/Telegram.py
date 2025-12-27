# ======================================================
# © 2025-26 Purvi Bots | MIT License
# Developer : @TheSigmaCoder
# ======================================================

import asyncio
import os
import re
import json
import random
import aiohttp
import yt_dlp

from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

from PurviBots.utils.database import is_on_off
from PurviBots.utils.formatters import time_to_seconds

from os import getenv

API_URL = getenv("API_URL", "https://pytdbotapi.thequickearn.xyz")
VIDEO_API_URL = getenv("VIDEO_API_URL", "https://api.video.thequickearn.xyz")
API_KEY = getenv("API_KEY", "YOUR_KEY")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# -------------------- COOKIES --------------------

def cookie_txt_file():
    path = "cookies"
    if not os.path.exists(path):
        return None
    files = [f for f in os.listdir(path) if f.endswith(".txt")]
    return os.path.join(path, random.choice(files)) if files else None


# -------------------- API AUDIO --------------------

async def download_song(link: str):
    video_id = link.split("v=")[-1].split("&")[0]
    file_path = f"{DOWNLOAD_DIR}/{video_id}.mp3"

    if os.path.exists(file_path):
        return file_path

    api_url = f"{API_URL}/song/{video_id}?api={API_KEY}"

    async with aiohttp.ClientSession() as session:
        for _ in range(10):
            async with session.get(api_url) as r:
                data = await r.json()
                if data.get("status") == "done":
                    url = data["link"]
                    async with session.get(url) as f:
                        with open(file_path, "wb") as out:
                            out.write(await f.read())
                    return file_path
                await asyncio.sleep(4)

    return None


# -------------------- API VIDEO --------------------

async def download_video(link: str):
    video_id = link.split("v=")[-1].split("&")[0]
    file_path = f"{DOWNLOAD_DIR}/{video_id}.mp4"

    if os.path.exists(file_path):
        return file_path

    api_url = f"{VIDEO_API_URL}/video/{video_id}?api={API_KEY}"

    async with aiohttp.ClientSession() as session:
        for _ in range(10):
            async with session.get(api_url) as r:
                data = await r.json()
                if data.get("status") == "done":
                    url = data["link"]
                    async with session.get(url) as f:
                        with open(file_path, "wb") as out:
                            out.write(await f.read())
                    return file_path
                await asyncio.sleep(6)

    return None


# -------------------- FILE SIZE CHECK --------------------

async def check_file_size(link):
    cookie = cookie_txt_file()
    if not cookie:
        return None

    proc = await asyncio.create_subprocess_exec(
        "yt-dlp", "--cookies", cookie, "-J", link,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    out, _ = await proc.communicate()
    data = json.loads(out.decode())
    return sum(f.get("filesize", 0) for f in data.get("formats", []))


# -------------------- YOUTUBE API --------------------

class YouTubeAPI:

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(youtube\.com|youtu\.be)"

    async def url(self, message: Message):
        for msg in [message, message.reply_to_message]:
            if not msg:
                continue
            if msg.entities:
                for e in msg.entities:
                    if e.type == MessageEntityType.URL:
                        return msg.text[e.offset:e.offset + e.length]
        return None

    async def details(self, link):
        r = VideosSearch(link, limit=1)
        v = (await r.next())["result"][0]
        return (
            v["title"],
            v["duration"],
            int(time_to_seconds(v["duration"])) if v["duration"] else 0,
            v["thumbnails"][0]["url"],
            v["id"],
        )

    async def download(self, link, video=False, audio=False):
        if audio:
            return await download_song(link), True

        if video:
            file = await download_video(link)
            if file:
                return file, True

            size = await check_file_size(link)
            if size and size / (1024 * 1024) > 250:
                return None, None

            cookie = cookie_txt_file()
            if not cookie:
                return None, None

            proc = await asyncio.create_subprocess_exec(
                "yt-dlp", "--cookies", cookie, "-f",
                "best[height<=720]", "-o",
                f"{DOWNLOAD_DIR}/%(id)s.%(ext)s", link
            )
            await proc.communicate()
            return True, False

        return None, None
