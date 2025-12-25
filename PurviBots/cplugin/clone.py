import time
import random
from datetime import datetime

import psutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from PurviBots import app
from config import PING_IMG_URL, STREAMI_PICS
from .utils import StartTime
from PurviBots.utils import get_readable_time
from PurviBots.utils.decorators.language import language

APP_LINK = f"https://t.me/Suhani_Music_Robot"


@Client.on_message(filters.command("clone"))
@language
async def ping_clone(client: Client, message: Message, _):
    bot = await client.get_me()


    hmm = await message.reply_photo(
        photo=random.choice(STREAMI_PICS), caption=_["NO_CLONE_MSG"],
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ɢᴏ ᴀɴᴅ ᴄʟᴏɴᴇ", url=APP_LINK)]
            ]
        )
    )
