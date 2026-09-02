import asyncio
import os
from threading import Thread
from flask import Flask, redirect
from pyrogram import Client, enums, filters
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest
from config import API_HASH, API_ID, BOT_TOKEN, BOT_USERNAME, FORCE_SUB_CHANNEL, OWNER_ID
from functions import (
    blacklist_db,
    groups,
    init_vivbot_id,
    process_auto_delete,
    users,
)



# Clients Definition
bot = Client("deletebot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vivbot = TelegramClient("vivbot_session", API_ID, API_HASH)



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




@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

   
    try:
        member = await bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
            btn = [[InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔒", url=f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}")],
                   [InlineKeyboardButton("Jᴏɪɴᴇᴅ 🔑", callback_data="check_join")]]
            await message.reply("<i>Join Updates Channel to use me 🔐.</i>", parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
            return
    except Exception:
        btn = [[InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔒", url=f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}")],
               [InlineKeyboardButton("Jᴏɪɴᴇᴅ 🔑", callback_data="check_join")]]
        await message.reply("<i>Join Updates Channel to use me 🔐.</i>", parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(btn))
        return

   
    await users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

   
    buttons = [
        [InlineKeyboardButton("➕ Add Me To Group", url=f"http://t.me/{BOT_USERNAME}?startgroup=none&admin=delete_messages+invite_users")],
        [InlineKeyboardButton("❔ Help", callback_data="help"), InlineKeyboardButton("❕About", callback_data="about")]
    ]
    
    welcome_text = (
        f"Hello **{first_name}**👋\n\n"
        f"I am **Anti-Promotion** Shield.\n"
        f"I can help protect groups from **promotion**,\n"
        f"and blacklisted bots.\n"
        f"Check ❔ Help menu for more details\n\n"
        f"💬 Support: soon"
    )
    
    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )



@bot.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user_id = query.from_user.id
    first_name = query.from_user.first_name

   
    if query.data == "check_join":
        try:
            member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
            if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                await query.answer("❌ You haven't joined the channel yet.", show_alert=True)
                return
        except Exception:
            await query.answer("❌ Join channel first.", show_alert=True)
            return

        await query.answer("✅ Verification successful")
        await users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
        query.data = "back"

    # Help Menu Button Click
    if query.data == "help":
        help_text = (
            "🚫 **Anti-Promotion Help **❔\n\n"
            "Usage:\n"
            "    /addbot - Add a bot to blacklist\n"
            "    /delbot - Remove a bot from blacklist\n"
            "    /botlist - View blacklisted bots\n\n"
            "❕ Note: Only admins can use these commands."
        )
        await query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    # About Menu Button Click
    elif query.data == "about":
        about_text = (
            f"<blockquote>ℹ️ About Anti-Promotion Shield</blockquote>\n\n"
            f"🤖 Version : 1.0.0\n"
            f"📝 Language : Python\n"
            f"📚 Library : Pyrogram\n"
            f"☁️ Server : VPS\n"
            f"💬 Support : t.me/RMB0T?direct\n"
            f"📢 Updates : @RMB0T\n"
            f"👤 Total users : 4852\n"
            f"👥 Protected chats : 486"
        )
        await query.message.edit_text(
            about_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Me To Group", url=f"http://t.me/{BOT_USERNAME}?startgroup=none&admin=delete_messages+invite_users")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ]),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    # Back to Menu Button Click
    elif query.data == "back":
        buttons = [
            [InlineKeyboardButton("➕ Add Me To Group", url=f"http://t.me/{BOT_USERNAME}?startgroup=none&admin=delete_messages+invite_users")],
            [InlineKeyboardButton("❔ Help", callback_data="help"), InlineKeyboardButton("❕About", callback_data="about")]
        ]
        welcome_text = (
            f"Hello **{first_name}**👋\n\n"
            f"I am **Anti-Promotion** Shield.\n"
            f"I can help protect groups from **promotion**,\n"
            f"and blacklisted bots.\n"
            f"Check ❔ Help menu for more details\n\n"
            f"💬 Support: soon"
        )
        await query.message.edit_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN
        )






async def ensure_vivbot_joined(bot, vivbot, chat_id):
    """
    Safely handles vivbot group joining. Verifies membership first.
    If the main bot lacks invite link permissions, it alerts the group chat.
    """
    try:
        global vivbot_ID
        if vivbot_ID:
            try:
                check_member = await vivbot.get_participants(chat_id, filter=None, search=str(vivbot_ID))
                if check_member:
                    print(f"ℹ️ vivbot is already a member of Chat={chat_id}. Skipping invite request.")
                    return True  
            except Exception:
                pass  

        try:
            chat = await bot.get_chat(chat_id)
            invite_link = chat.invite_link
            
            if not invite_link:
                invite_link = await bot.export_chat_invite_link(chat_id)
                
        except ChatAdminRequired:
            print(f"❌ Failed to generate link: Main Bot lacks admin permissions in Chat={chat_id}")
            
            alert_text = (
                "⚠️ **Security System Alert**\n\n"
                "🤖 I need the **Invite Users via Link** (Add Users) admin permission to bring my Assistant vivbot into this group.\n\n"
                "💡 *Please grant me this permission so the Anti-Promotion shield can fully protect your group!*"
            )
            try:
                await bot.send_message(chat_id, alert_text)
            except Exception as e:
                print(f"Could not send alert message to chat: {e}")
                
            return "admin_required"
        invite_hash = invite_link.split('+')[-1] if '+' in invite_link else invite_link.split('/')[-1]

        try:
            await vivbot(ImportChatInviteRequest(invite_hash))
            print(f"✅ Telethon vivbot successfully joined Chat={chat_id} via invite link.")
            return True
        except UserAlreadyParticipantError:
            print(f"ℹ️ Telethon caught: Already a member of Chat={chat_id}. Limit saved.")
            return True
        except FloodWaitError as e:
            print(f"⚠️ Telegram Rate Limit hit! Must wait {e.seconds} seconds.")
            return f"flood_wait_{e.seconds}"

    except Exception as e:
        print(f"❌ vivbot join function failed: {e}")
        return str(e)







@bot.on_message(filters.new_chat_members)
async def welcome_and_invite_vivbot(client, message):
    me = await client.get_me()
    bot_added = any(user.id == me.id for user in message.new_chat_members)
    
    if bot_added:
        await ensure_vivbot_joined(bot=bot, vivbot=vivbot, chat_id=message.chat.id)








    

@bot.on_message(filters.command("addbot") & filters.group)
async def add_bot_to_blacklist(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Admin check
    is_admin = False
    async for m in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if m.user.id == user_id:
            is_admin = True
            break
    if not is_admin: return

    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** `/addbot @username_of_bot`")
    await ensure_vivbot_joined(bot=bot, vivbot=vivbot, chat_id=message.chat.id)
    target_bot = message.command[1].lower().replace("@", "")
    
    await blacklist_db.update_one(
        {"username": target_bot, "group_id": chat_id}, 
        {"$set": {"username": target_bot, "group_id": chat_id}}, 
        upsert=True
    )
    await message.reply(f"🚫 @{target_bot} **added to this group's anti-promotion blocklist!**")


@bot.on_message(filters.command("delbot") & filters.group)
async def remove_bot_from_blacklist(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    is_admin = False
    async for m in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if m.user.id == user_id:
            is_admin = True
            break
    if not is_admin: return

    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** `/delbot @username_of_bot`")

    target_bot = message.command[1].lower().replace("@", "")
    
    res = await blacklist_db.delete_one({"username": target_bot, "group_id": chat_id})
    if res.deleted_count > 0:
        await message.reply(f"✅ @{target_bot} **removed from this group's blocklist.**")
    else:
        await message.reply("❌ That bot is not on this group's blocklist.")


@bot.on_message(filters.command("botlist") & filters.group)
async def view_blacklisted_bots(client, message: Message):
    chat_id = message.chat.id
    text = "📋 **Anti-Promotion Blocked Bots (This Group):**\n\n"
    count = 0
    
    async for b in blacklist_db.find({"group_id": chat_id}):
        count += 1
        text += f"{count}. @{b['username']}\n"
        
    if count == 0:
        text = "🏖 **The bot blocklist is currently empty in this group.**"
        
    await message.reply(text)


@bot.on_message(filters.group & ~filters.service)
async def pyrogram_handler(client, message: Message):
    if message.from_user and message.from_user.is_bot:
        await process_auto_delete(vivbot, bot, message.chat.id, message.id, None, message.from_user.username, None)
        return

    sender_id = message.from_user.id if message.from_user else None
    sender_username = message.from_user.username if message.from_user else None

    async def check_admin():
        if not sender_id: return False
        member = await client.get_chat_member(message.chat.id, sender_id)
        return member.status.value in ["administrator", "owner"]

    await process_auto_delete(vivbot, bot, message.chat.id, message.id, sender_id, sender_username, check_admin)





@vivbot.on(events.NewMessage())
async def telethon_handler(event):
    if not event.is_group: return
    try:
        sender = await event.get_sender()
    except Exception:
        sender = None

    is_bot = getattr(sender, 'bot', False)
    sender_username = getattr(sender, 'username', None)
    sender_id = sender.id if sender else None

    if is_bot or sender_username:
        async def check_admin():
            if not sender_id: return False
            perms = await vivbot.get_permissions(event.chat_id, sender_id)
            return perms.is_admin
        await process_auto_delete(vivbot, bot, event.chat_id, event.message.id, sender_id, sender_username, check_admin)





@bot.on_message(filters.command("broadcast") & filters.private)
async def user_broadcast(_, message):
    if message.from_user.id != OWNER_ID: return
    if len(message.command) < 2: return
    text = message.text.split(None, 1)[1]
    sent, failed = 0, 0
    async for user in users.find({}):
        try:
            await bot.send_message(user["user_id"], text)
            sent += 1
            await asyncio.sleep(0.1)
        except FloodWait as e: await asyncio.sleep(e.value)
        except: failed += 1
    await message.reply(f"✅ Broadcast sent to {sent} users.\n❌ Failed: {failed}")

@bot.on_message(filters.command("users") & filters.private)
async def total_users(_, message):
    if message.from_user.id != OWNER_ID: return
    total = await users.count_documents({})
    await message.reply(f"👤 Total users: `{total}`", parse_mode=enums.ParseMode.MARKDOWN)

@bot.on_message(filters.command("g_broadcast") & filters.private)
async def group_broadcast(_, message):
    if message.from_user.id != OWNER_ID: return
    if len(message.command) < 2: return
    text = message.text.split(None, 1)[1]
    success, fail = 0, 0
    async for group in groups.find({}):
        try:
            await bot.send_message(group["group_id"], text)
            success += 1
        except: fail += 1
    await message.reply(f"✅ Broadcast completed.\nSent: {success}, Failed: {fail}")

# Flask Keep-Alive
flask_app = Flask(__name__)
@flask_app.route('/')
def index(): return redirect(f"https://t.me/{BOT_USERNAME}", code=302)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))


async def main():
    print("⚡ Starting services...")
    await vivbot.start()
    
   
    await init_vivbot_id(vivbot) 
    print("✅ Telethon vivbot initialized!")
    
    await bot.start()
    print("✅ Pyrogram Bot initialized!")
    
    await asyncio.gather(
        vivbot.run_until_disconnected(),
        bot.idle() if hasattr(bot, 'idle') else asyncio.Event().wait()
    )

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())