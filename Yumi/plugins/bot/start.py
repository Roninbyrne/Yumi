import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import config
from Yumi import app
from Yumi.misc import _boot_
from Yumi.plugins.sudo.sudoers import sudoers_list
from Yumi.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    is_banned_user,
    is_on_off,
)
from Yumi.utils.decorators.language import LanguageStart
from Yumi.utils.formatters import get_readable_time
from Yumi.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# Define the get_lang function
async def get_lang(chat_id):
    # Placeholder logic: Replace with actual logic to fetch the language from the database
    return 'en'  # Default to English

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await app.send_message(
        chat_id=config.LOGGER_ID,
        text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
    )

    out = private_panel(_)
    await message.reply(f" нєу {message.from_user.first_name} <a href='{config.START_VIDEO}'>🌀</a>")
    await message.reply(f"<b>๏ 𝙷𝚎𝚢 𝚝𝚑𝚎𝚛𝚎! 𝙸'𝚖 {app.mention} 𝙱𝚘𝚝! \n๏ ᴀ ʟᴀᴛᴇꜱᴛ ᴍᴜꜱɪᴄ ʙᴏᴛ ꜰᴏʀ ᴘʟᴀʏɪɴɢ ꜱᴏɴɢꜱ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs</b>", reply_markup=InlineKeyboardMarkup(out))

    if await is_on_off(2):
        return await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
        )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply(text=f"{app.mention} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ.\n\n<b>✫ ᴜᴘᴛɪᴍᴇ :</b> {get_readable_time(uptime)}<a href='{config.PING_IMG_URL}'> .</a>",
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply(
                    text=f"ʜᴇʏ {message.from_user.first_name},\nᴛʜɪs ɪs {app.mention}\n\nᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ {message.chat.title}, {app.mention} ᴄᴀɴ ɴᴏᴡ ᴩʟᴀʏ sᴏɴɢs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.<a href='https://telegra.ph/file/8eaf615030d0af86dde19.mp4'> .</a>",
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await add_served_chat(message.chat.id)
                await client.send_message(config.LOGGER_ID,
                    text=f"""ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ {message.chat.title}
                    {app.mention} ᴄᴀɴ ɴᴏᴡ ᴩʟᴀʏ sᴏɴɢs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.-
                    ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ """)
                await message.stop_propagation()

        except Exception as ex:
            print(ex)