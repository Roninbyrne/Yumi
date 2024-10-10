import asyncio

from pyrogram import idle

import config
from Yumi.plugins.bot import help
from Yumi import LOGGER, app
from Yumi.misc import sudo
from Yumi.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from Yumi.plugins.bot import help
from Yumi.plugins.bot import start
from Yumi.plugins.misc import broadcast
from Yumi.plugins.sudo import blchat, block, gban, restart, sudoers 
from Yumi.plugins.tools import dev, language, ping


async def init():
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).error(f"Error fetching banned users: {e}")

    await app.start()

    LOGGER("Yumi.plugins").info("Successfully Imported Modules...")

    LOGGER("Yumi").info(
        "\x41\x6e\x6f\x6e\x58\x20\x4d\x75\x73\x69\x63\x20\x42\x6f\x74\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\n\n\x44\x6f\x6e'\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x46\x61\x6c\x6c\x65\x6e\x41\x73\x73\x6f\x63\x69\x61\x74\x69\x6f\x6e"
    )

    await idle()
    await app.stop()
    LOGGER("Yumi").info("Stopping Yumi Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())