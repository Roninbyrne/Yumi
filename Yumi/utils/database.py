import random
from typing import Dict, List, Union

from Yumi.core.mongo import mongodb

blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
gbansdb = mongodb.gban
langdb = mongodb.language
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb

async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return user is not None

async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def add_served_user(user_id: int):
    if await is_served_user(user_id):
        return
    return await usersdb.insert_one({"user_id": user_id})

async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return chat is not None

async def add_served_chat(chat_id: int):
    if await is_served_chat(chat_id):
        return
    return await chatsdb.insert_one({"chat_id": chat_id})

async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_chatdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list

async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False

async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False

async def get_gbanned() -> list:
    results = []
    async for user in gbansdb.find({"user_id": {"$gt": 0}}):
        results.append(user["user_id"])
    return results

async def is_gbanned_user(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    return user is not None

async def add_gban_user(user_id: int):
    if await is_gbanned_user(user_id):
        return
    return await gbansdb.insert_one({"user_id": user_id})

async def remove_gban_user(user_id: int):
    if not await is_gbanned_user(user_id):
        return
    return await gbansdb.delete_one({"user_id": user_id})

async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    return sudoers["sudoers"] if sudoers else []

async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True

async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True

async def get_banned_users() -> list:
    results = []
    async for user in blockeddb.find({"user_id": {"$gt": 0}}):
        results.append(user["user_id"])
    return results

async def get_banned_count() -> int:
    users = await blockeddb.find({"user_id": {"$gt": 0}}).to_list(length=100000)
    return len(users)

async def is_banned_user(user_id: int) -> bool:
    user = await blockeddb.find_one({"user_id": user_id})
    return user is not None

async def add_banned_user(user_id: int):
    if await is_banned_user(user_id):
        return
    return await blockeddb.insert_one({"user_id": user_id})

async def remove_banned_user(user_id: int):
    if not await is_banned_user(user_id):
        return
    return await blockeddb.delete_one({"user_id": user_id})

async def is_on_off(feature_id: int) -> bool:
    """
    Check if a specific feature is enabled or disabled.

    Parameters:
        feature_id (int): The ID of the feature to check.

    Returns:
        bool: True if the feature is enabled, False otherwise.
    """
    feature = await langdb.find_one({"feature_id": feature_id})
    return feature is not None and feature.get("enabled", False)