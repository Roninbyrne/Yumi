from pyrogram import Client, filters
from Yumi import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from datetime import datetime, timedelta
import asyncio
import time
import logging
from config import MONGO_DB_URI, Helpers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client['my_bot_db']
user_states_collection = db['user_states']
video_channels_collection = db['video_channels']
subscriptions_col = db['user_subscriptions']

user_command_times = {}

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

def is_user_allowed(user_id):
    subscription = get_subscription(user_id)
    if not subscription:
        return False

    start_date = subscription["start_date"]
    months_subscribed = subscription["months_subscribed"]
    expiration_date = start_date + timedelta(days=months_subscribed * 30)

    return datetime.now() <= expiration_date

def is_rate_limited(user_id, command, cooldown_time=60):
    current_time = time.time()
    last_command_time = user_command_times.get(user_id, {}).get(command)

    if last_command_time and current_time - last_command_time < cooldown_time:
        return True
    user_command_times.setdefault(user_id, {})[command] = current_time
    return False

async def notify_expiring_subscriptions():
    while True:
        for subscription in list(subscriptions_col.find()):
            user_id = subscription["user_id"]
            start_date = subscription["start_date"]
            months_subscribed = subscription["months_subscribed"]
            expiration_date = start_date + timedelta(days=months_subscribed * 30)
            time_remaining = expiration_date - datetime.now()

            if timedelta(hours=23) < time_remaining < timedelta(hours=24):
                await app.send_message(user_id, f"⚠️ Your subscription will expire in 24 hours. Renew now to continue enjoying the bot's services!")

            if time_remaining <= timedelta(0):
                await app.send_message(user_id, "❌ Your subscription has expired. Please contact support to renew.")
                remove_subscription(user_id)

        await asyncio.sleep(3600)

@app.on_message(filters.command("upload") & filters.private)
async def upload_video(client, message):
    user_id = message.chat.id
    if not is_user_allowed(user_id):
        await client.send_message(user_id, "❌ You do not have an active subscription. Please renew to use this feature.")
        return

    command_params = message.text.split(" ")
    if len(command_params) < 3:
        await client.send_message(message.chat.id, "Usage: /upload <public_channel> <private_channel>")
        return

    public_channel, private_channel = command_params[1], command_params[2]

    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {
            "step": "get_video_link",
            "public_channel": public_channel,
            "private_channel": private_channel
        }},
        upsert=True
    )
    await client.send_message(message.chat.id, "Please send the video message link.")

@app.on_message(filters.private)
async def handle_messages(client, message):
    user_id = message.chat.id
    user_state = user_states_collection.find_one({"user_id": user_id})

    if user_state:
        state = user_state.get("step")

        if state == "get_video_link":
            await get_video_link(client, message)
        elif state == "get_description":
            await get_description(client, message)
        elif state == "get_cover_photo":
            await get_cover_photo(client, message)

async def get_video_link(client, message):
    video_link = message.text
    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {"video_link": video_link, "step": "get_description"}}
    )
    await client.send_message(message.chat.id, "Great! Now please provide a description for the video. Make it engaging to attract viewers!")

async def get_description(client, message):
    description = message.text
    user_states_collection.update_one(
        {"user_id": message.chat.id},
        {"$set": {"description": description, "step": "get_cover_photo"}}
    )
    await client.send_message(message.chat.id, "Please send the cover photo.")

async def get_cover_photo(client, message):
    if message.photo:
        cover_photo = message.photo.file_id
        user_state = user_states_collection.find_one({"user_id": message.chat.id})

        video_link = user_state.get("video_link")
        description = user_state.get("description")
        public_channel = user_state.get("public_channel")
        private_channel = user_state.get("private_channel")

        video_id = video_link.split('/')[-1]
        await post_video_to_channel(public_channel, video_id, description, cover_photo)

        video_channels_collection.update_one(
            {"video_id": video_id},
            {"$set": {
                "public_channel": public_channel,
                "private_channel": private_channel
            }},
            upsert=True
        )

        await client.send_message(message.chat.id, "Video details uploaded to the public channel!")

async def post_video_to_channel(public_channel, video_id, description, cover_photo):
    button = InlineKeyboardMarkup([[InlineKeyboardButton("✯ ᴅᴏᴡɴʟᴏᴀᴅ ✯", callback_data=video_id)]])

    await app.send_photo(
        chat_id=public_channel,
        photo=cover_photo,
        caption=f"{description}\n\n❱ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ<a href='https://t.me/phoenixXsupport'> [ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a>",
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

            await callback_query.answer("Fetching your request... Please check your DM.", show_alert=True)
            await client.send_message(user_id, "Please forward this video or file in your saved messages and download there, the content will be deleted after 5 minutes.")
            await asyncio.sleep(300)
            await client.delete_messages(user_id, sent_message.id)
        else:
            await callback_query.answer("Content not found or it's not a video/file message.", show_alert=True)
    except Exception as e:
        await callback_query.answer("Failed to retrieve content, please try again later.", show_alert=True)
        logger.error(f"Error fetching content: {e}")

@app.on_message(filters.command("addmmbr") & filters.user(Helpers))
async def add_member(client, message):
    try:
        command_params = message.text.split(" ")
        if len(command_params) < 3:
            await client.send_message(message.chat.id, "Usage: /addmmbr <username/UserID/reply to user> <months>")
            return

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        else:
            if command_params[1].isdigit():
                target_user = int(command_params[1])
                target_name = (await client.get_users(target_user)).first_name
            else:
                target_user = (await client.get_users(command_params[1])).id
                target_name = (await client.get_users(target_user)).first_name

        months_subscribed = int(command_params[2])
        start_date = datetime.now()

        add_subscription(target_user, start_date, months_subscribed)

        await client.send_message(message.chat.id, f"User {target_name} has been added with a {months_subscribed}-month subscription.")
        await client.send_message(target_user, f"🎉 You have been granted access to the bot for {months_subscribed} month(s).")
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}")

@app.on_message(filters.command("status"))
async def subscription_status(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    subscription = get_subscription(user_id)

    if not subscription:
        await client.send_message(chat_id, "❌ You do not have an active subscription.")
        return

    start_date = subscription["start_date"]
    months_subscribed = subscription["months_subscribed"]
    expiration_date = start_date + timedelta(days=months_subscribed * 30)
    time_remaining = expiration_date - datetime.now()

    if time_remaining.total_seconds() <= 0:
        await client.send_message(chat_id, "❌ Your subscription has expired.")
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

    await client.send_message(chat_id, status_message)

@app.on_message(filters.command("rmmbr") & filters.user(Helpers))
async def remove_member(client, message):
    try:
        command_params = message.text.split(" ")
        if len(command_params) < 2:
            await client.send_message(message.chat.id, "Usage: /rmmbr <username/UserID>")
            return

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        else:
            target_user = int(command_params[1]) if command_params[1].isdigit() else (await client.get_users(command_params[1])).id
            target_name = (await client.get_users(target_user)).first_name

        if get_subscription(target_user):
            remove_subscription(target_user)
            await client.send_message(message.chat.id, f"User {target_name} has been removed from the subscription list.")
            await client.send_message(target_user, "❌ Your subscription has been manually revoked by an admin.")
        else:
            await client.send_message(message.chat.id, f"User {target_name} is not in the subscription list.")
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}")

@app.on_message(filters.command("mmbrlist") & filters.user(Helpers))
async def list_members(client, message):
    subscribers = list(subscriptions_col.find())
    if not subscribers:
        await client.send_message(message.chat.id, "No users are currently subscribed.")
        return

    member_list = "📝 **Subscribed Users:**\n\n"
    for subscription in subscribers:
        user_id = subscription["user_id"]
        start_date = subscription["start_date"]
        months_subscribed = subscription["months_subscribed"]
        expiration_date = start_date + timedelta(days=months_subscribed * 30)
        time_remaining = expiration_date - datetime.now()

        user_info = await client.get_users(user_id)
        member_list += f"**{user_info.first_name}** (ID: {user_id})\n"
        member_list += f"Time remaining: {time_remaining.days} days, {time_remaining.seconds // 3600} hours, and {(time_remaining.seconds // 60) % 60} minutes\n\n"

    await client.send_message(message.chat.id, member_list)

async def start_periodic_task():
    asyncio.create_task(notify_expiring_subscriptions())

if __name__ == "__main__":
    app.run(start_periodic_task())