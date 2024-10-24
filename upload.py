from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH

app = Client("my_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from datetime import datetime, timedelta
import asyncio
from config import MONGO_DB_URI, Helpers

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client['my_bot_db']
user_states_collection = db['user_states']
video_channels_collection = db['video_channels']
subscriptions_col = db['user_subscriptions']

def get_subscription(user_id):
    return subscriptions_col.find_one({"user_id": user_id})

def add_subscription(user_id, start_date, months_subscribed):
    subscriptions_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "start_date": start_date,
                "months_subscribed": months_subscribed
            }
        },
        upsert=True
    )

def remove_subscription(user_id):
    subscriptions_col.delete_one({"user_id": user_id})

@app.on_message(filters.command("upload"))
def upload_video(client, message):
    user_id = message.chat.id
    if not is_user_allowed(user_id):
        client.send_message(user_id, "❌ You do not have an active subscription. Please renew to use this feature.")
        return

    try:
        command_params = message.text.split(" ")
        public_channel = command_params[1]
        private_channel = command_params[2]
    except IndexError:
        client.send_message(message.chat.id, "Usage: /upload <public_channel> <private_channel>")
        return

    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {
            "step": "get_video_link",
            "public_channel": public_channel,
            "private_channel": private_channel
        }},
        upsert=True
    )
    client.send_message(message.chat.id, "Please send the video message link.")

def is_user_allowed(user_id):
    subscription = get_subscription(user_id)
    if not subscription:
        return False

    start_date = subscription["start_date"]
    months_subscribed = subscription["months_subscribed"]
    expiration_date = start_date + timedelta(days=months_subscribed * 30)

    return datetime.now() <= expiration_date

@app.on_message(filters.private)
def handle_messages(client, message):
    user_id = message.chat.id
    user_state = user_states_collection.find_one({"user_id": user_id})

    if user_state:
        state = user_state.get("step")

        if state == "get_video_link":
            get_video_link(client, message)
        elif state == "get_description":
            get_description(client, message)
        elif state == "get_cover_photo":
            get_cover_photo(client, message)

def get_video_link(client, message):
    video_link = message.text
    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {"video_link": video_link, "step": "get_description"}}
    )
    client.send_message(message.chat.id, "Please provide a description.")

def get_description(client, message):
    description = message.text
    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {"description": description, "step": "get_cover_photo"}}
    )
    client.send_message(message.chat.id, "Please send the cover photo.")

def get_cover_photo(client, message):
    if message.photo:
        cover_photo = message.photo.file_id
        user_state = user_states_collection.find_one({"user_id": message.chat.id})

        video_link = user_state.get("video_link")
        description = user_state.get("description")
        public_channel = user_state.get("public_channel")
        private_channel = user_state.get("private_channel")

        video_id = video_link.split('/')[-1]
        post_video_to_channel(public_channel, video_id, description, cover_photo)

        video_channels_collection.update_one(
            {"video_id": video_id},
            {"$set": {
                "public_channel": public_channel,
                "private_channel": private_channel
            }},
            upsert=True
        )

        client.send_message(message.chat.id, "Video details uploaded to the public channel!")

def post_video_to_channel(public_channel, video_id, description, cover_photo):
    button = InlineKeyboardMarkup([[InlineKeyboardButton("✯ ᴅᴏᴡɴʟᴏᴀᴅ ✯", callback_data=video_id)]])

    app.send_photo(
        chat_id=public_channel,
        photo=cover_photo,
        caption=f"{description}\n\n❱ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ<a href='https://t.me/mystic_legion'> [ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a>",
        reply_markup=button
    )

@app.on_callback_query()
async def handle_button_click(client, callback_query):
    video_id = callback_query.data
    user_id = callback_query.from_user.id

    video_info = video_channels_collection.find_one({"video_id": video_id})

    if not video_info:
        await callback_query.answer("Video not found. Please try uploading again.", show_alert=True)
        return

    private_channel = video_info["private_channel"]

    try:
        message = await client.get_messages(private_channel, int(video_id))
        if message:
            if message.video:
                file_id = message.video.file_id
                sent_message = await client.send_video(user_id, file_id)
            elif message.document:
                file_id = message.document.file_id
                sent_message = await client.send_document(user_id, file_id)

            await callback_query.answer("ꜰᴇᴛᴄʜɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ.... ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʙᴏᴛ ᴀʀᴏɴᴀ ᴅᴍ", show_alert=True)
            await client.send_message(user_id, "ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜɪꜱ ᴠɪᴅᴇᴏ ᴏʀ ꜰɪʟᴇ ɪɴ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇʀᴇ, ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ 5 ᴍɪɴᴜᴛᴇꜱ .")
            await asyncio.sleep(300)
            await client.delete_messages(user_id, sent_message.id)
        else:
            await callback_query.answer("ᴄᴏɴᴛᴇɴᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ɪᴛꜱ ɴᴏᴛ ᴀ ᴠɪᴅᴇᴏ ᴏʀ ꜰɪʟᴇ ᴍᴇꜱꜱᴀɢᴇ.", show_alert=True)
    except Exception as e:
        await callback_query.answer("ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴄᴏɴᴛᴇɴᴛ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
        print(f"Error fetching content: {e}")

async def notify_expiring_subscriptions():
    while True:
        for subscription in list(subscriptions_col.find()):
            user_id = subscription["user_id"]
            start_date = subscription["start_date"]
            months_subscribed = subscription["months_subscribed"]
            expiration_date = start_date + timedelta(days=months_subscribed * 30)
            time_remaining = expiration_date - datetime.now()

            if timedelta(hours=23) < time_remaining < timedelta(hours=24):
                await app.send_message(user_id, "⚠️ Your subscription is expiring in 24 hours!")

            if time_remaining <= timedelta(0):
                await app.send_message(user_id, "❌ Your subscription has expired. Please contact support for renewal.")
                remove_subscription(user_id)

        await asyncio.sleep(3600)

@app.on_message(filters.command("addmmbr") & filters.user(Helpers))
def add_member(client, message):
    try:
        command_params = message.text.split(" ")
        if len(command_params) < 3:
            client.send_message(message.chat.id, "Usage: /addmmbr <username/UserID/reply to user> <months>")
            return

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        else:
            target_user = int(command_params[1]) if command_params[1].isdigit() else client.get_users(command_params[1]).id
            target_name = client.get_users(target_user).first_name

        months_subscribed = int(command_params[2])
        start_date = datetime.now()

        add_subscription(target_user, start_date, months_subscribed)

        client.send_message(message.chat.id, f"User {target_name} has been added with a {months_subscribed}-month subscription.")
        client.send_message(target_user, f"🎉 You have been granted access to the bot for {months_subscribed} month(s).")
    except Exception as e:
        client.send_message(message.chat.id, f"Error: {e}")

@app.on_message(filters.command("status"))
def subscription_status(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    subscription = get_subscription(user_id)

    if not subscription:
        client.send_message(chat_id, "❌ You do not have an active subscription.")
        return

    start_date = subscription["start_date"]
    months_subscribed = subscription["months_subscribed"]
    expiration_date = start_date + timedelta(days=months_subscribed * 30)
    time_remaining = expiration_date - datetime.now()

    if time_remaining.total_seconds() <= 0:
        client.send_message(chat_id, "❌ Your subscription has expired.")
        return

    months_left = time_remaining.days // 30
    days_left = time_remaining.days % 30
    hours_left = (time_remaining.seconds // 3600)
    minutes_left = (time_remaining.seconds // 60) % 60

    status_message = (
        f"🗓️ Subscription Status for {message.from_user.first_name}:\n"
        f"Start Date: {start_date.strftime('%Y-%m-%d')}\n"
        f"Months Subscribed: {months_subscribed}\n"
        f"Time Remaining: {months_left} months, {days_left} days, {hours_left} hours, {minutes_left} minutes\n"
    )

    client.send_message(chat_id, status_message)

@app.on_message(filters.command("removemmbr") & filters.user(Helpers))
def remove_member(client, message):
    try:
        command_params = message.text.split(" ")
        if len(command_params) < 2:
            client.send_message(message.chat.id, "Usage: /removemmbr <username/UserID>")
            return

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        else:
            target_user = int(command_params[1]) if command_params[1].isdigit() else client.get_users(command_params[1]).id
            target_name = client.get_users(target_user).first_name

        if get_subscription(target_user):
            remove_subscription(target_user)
            client.send_message(message.chat.id, f"User {target_name} has been removed from the subscription list.")
            client.send_message(target_user, "❌ Your subscription has been manually revoked by an admin.")
        else:
            client.send_message(message.chat.id, f"User {target_name} is not in the subscription list.")
    except Exception as e:
        client.send_message(message.chat.id, f"Error: {e}")

@app.on_message(filters.command("listmmbrs") & filters.user(Helpers))
def list_members(client, message):
    subscribers = list(subscriptions_col.find())
    if not subscribers:
        client.send_message(message.chat.id, "No users are currently subscribed.")
        return

    member_list = "📝 **Subscribed Users:**\n\n"
    for subscription in subscribers:
        user_id = subscription["user_id"]
        start_date = subscription["start_date"]
        months_subscribed = subscription["months_subscribed"]
        expiration_date = start_date + timedelta(days=months_subscribed * 30)
        time_remaining = expiration_date - datetime.now()

        user_info = client.get_users(user_id)
        member_list += f"**{user_info.first_name}** (ID: {user_id})\n"
        member_list += f"Time remaining: {time_remaining.days} days, {time_remaining.seconds // 3600} hours, and {(time_remaining.seconds // 60) % 60} minutes\n\n"

    client.send_message(message.chat.id, member_list)

async def start_periodic_task():
    asyncio.create_task(notify_expiring_subscriptions())

if __name__ == "__main__":
    app.run(start_periodic_task())
