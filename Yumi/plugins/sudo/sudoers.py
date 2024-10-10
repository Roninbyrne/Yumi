from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Yumi import app
from Yumi.misc import SUDOERS
from Yumi.utils.database import add_sudo, remove_sudo
from Yumi.utils.extraction import extract_user
from config import BANNED_USERS, OWNER_ID


# Example language data
LANGUAGE_DATA = {
    'en': {
        "general_1": "Please reply to a user to add them as sudo.",
        "sudo_1": "{} is already a sudo user.",
        "sudo_2": "{} has been added as a sudo user.",
        "sudo_3": "{} is not a sudo user.",
        "sudo_4": "{} has been removed from sudo users.",
        "sudo_5": "Sudo Users List:",
        "sudo_6": "Sudo Users:",
        "sudo_7": "No sudo users found.",
        "sudo_8": "An error occurred while processing."
    },
    # Add more languages as needed
}

# Define the language decorator
def language(func):
    async def wrapper(client, message: Message, *args, **kwargs):
        lang_code = 'en'  # Default language; can be adjusted based on user preferences
        _ = LANGUAGE_DATA[lang_code]  # Get language strings
        return await func(client, message, _, *args, **kwargs)
    return wrapper


@app.on_message(filters.command(["addsudo"]) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))
    added = await add_sudo(user.id)
    if added:
        SUDOERS.add(user.id)
        await message.reply_text(_["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))
    removed = await remove_sudo(user.id)
    if removed:
        SUDOERS.remove(user.id)
        await message.reply_text(_["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = _["sudo_5"]
    user = await app.get_users(OWNER_ID)
    user = user.first_name if not user.mention else user.mention
    text += f"1➤ {user}\n"
    count = 0
    smex = 0
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += _["sudo_6"]
                count += 1
                text += f"{count}➤ {user}\n"
            except:
                continue
    if not text:
        await message.reply_text(_["sudo_7"])
    else:
        close_button = InlineKeyboardButton("Close", callback_data="close")
        reply_markup = InlineKeyboardMarkup([[close_button]])
        await message.reply_text(text, reply_markup=reply_markup)