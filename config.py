
import os

API_ID = os.environ.get("API_ID","API")
API_HASH = os.environ.get("API_HASH","HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN","TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL","URL")

BOT_USERNAME = os.environ.get("BOT_USERNAME","BOT_USERNAME") # Without @
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "CHANNEL_USERNAME")  # without @
PORT = int(os.environ.get("PORT", 8080))
OWNER_ID = int(os.environ.get("OWNER_ID", "CHAT_ID")) 


GROUP_ID=-1004459 # group you want to monitor
LOG_CHANNEL_ID=-1003301 # group you want the logs to be posted to
LOGGER_BOT_TOKEN="Token" # bot the sends the logs (the bot should be able to send in the log channel)