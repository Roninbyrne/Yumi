from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app import app
from app import config

@app.on_message(filters.command(["start"]) & filters.private)
async def f_start(_, message):
    await message.reply(f"нєу {message.from_user.first_name} <a href='{config.START_VIDEO}'>☘️</a>")

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Support Chat", url=config.SUPPORT_CHAT)],
            [InlineKeyboardButton(text="Support Channel", url=config.SUPPORT_CHANNEL)],
            [InlineKeyboardButton(text="Owner", url=f"http://t.me/{config.OWNER_USERNAME}")],
            [InlineKeyboardButton(text="Add Me to Group", url=f"http://t.me/{config.BOT_USERNAME}?startgroup=true")],
        ]
    )

    await message.reply(
        f"<b>๏ 𝙷𝚎𝚢 𝚝𝚑𝚎𝚛𝚎! 𝙸'𝚖 {app.mention} 𝙱𝚘𝚝! \n"
        f"๏ 𝙸'𝚖 𝚊 𝚕𝚊𝚝𝚎𝚜𝚝 𝚋𝚘𝚝 𝚙𝚛𝚘𝚝𝚎𝚌𝚝𝚒𝚗𝚐 𝚢𝚘𝚞𝚛 𝚌𝚘𝚗𝚝𝚎𝚗𝚝 𝚏𝚛𝚘𝚖 𝚌𝚘𝚙𝚢𝚛𝚒𝚐𝚑𝚝 𝚙𝚘𝚜𝚝𝚒𝚗𝚐 𝚘𝚗 𝚌𝚑𝚊𝚗𝚗𝚎𝚕.\n"
        f"๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs</b>",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
