import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL



client = AsyncIOMotorClient(DATABASE_URL)
db = client['databas']
groups = db['group_id']
users = db['users']
blacklist_db = db['blacklist_bots']  


vivbot_ID = None

async def init_vivbot_id(vivbot_client):
    """Fetches and saves the vivbot ID globally at startup."""
    global vivbot_ID
    try:
        me = await vivbot_client.get_me()
        vivbot_ID = me.id
        print(f"✅ vivbot cached with ID: {vivbot_ID}")
    except Exception as e:
        print(f"❌ Failed to initialize vivbot cache: {e}")




async def process_auto_delete(vivbot, bot, chat_id, message_id, sender_id, sender_username, is_sender_admin_func):
    """
    Core Deletion Engine: Handles both scheduled regular deletions 
    and instant 0-second bans for blacklisted bots specific to each group.
    """
    try:
        if sender_username:
            clean_username = sender_username.lower().replace("@", "")
            is_blacklisted = await blacklist_db.find_one({"username": clean_username, "group_id": chat_id})
            if is_blacklisted:
                print(f"🚨 Blacklisted Bot detected: @{clean_username} in Chat={chat_id}. Deleting instantly!")
                await execute_deletion_routine(vivbot, bot, chat_id, message_id)
                return

        
        group = await groups.find_one({"group_id": chat_id})
        if not group or "delete_time" not in group:
            return

        delete_time = int(group["delete_time"])

       
        if sender_id and is_sender_admin_func:
            try:
                if await is_sender_admin_func():
                    return
            except Exception:
                pass

        
        await asyncio.sleep(delete_time)
        await execute_deletion_routine(vivbot, bot, chat_id, message_id)

    except Exception as e:
        print(f"Error in core engine execution: {e}")






async def execute_deletion_routine(vivbot, bot, chat_id, message_id):
    """Determines whether the vivbot or Pyrogram Bot should drop the hammer."""
    global vivbot_ID
    vivbot_success = False
    
    try:
        if vivbot_ID:
            
            check_member = await vivbot.get_participants(chat_id, filter=None, search=str(vivbot_ID))
            if check_member:
                await vivbot.delete_messages(chat_id, message_id)
                print(f"🗑 Deleted by vivbot | Chat={chat_id} Msg={message_id}")
                vivbot_success = True
    except Exception:
        vivbot_success = False

    if not vivbot_success:
        try:
            await bot.delete_messages(chat_id=chat_id, message_ids=message_id)
            print(f"🗑 Deleted by Pyrogram Bot | Chat={chat_id} Msg={message_id}")
        except Exception as bot_err:
            print(f"❌ Both clients failed to drop message {message_id}: {bot_err}")