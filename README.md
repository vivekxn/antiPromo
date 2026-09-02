# 🛡️ Anti-Promotion Shield Bot

A high-performance, hybrid Telegram moderation bot designed to protect groups from unsolicited promotions, spam links, and rogue bots. Built using **Pyrogram** for interactive UI, commands, and force-subscription, paired with a **Telethon** userbot assistant (`vivbot`) for automated group-joining and deep message inspection.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [How It Works](#-how-it-works)
- [Commands & Usage](#-commands--usage)
  - [Group Admin Commands](#group-admin-commands)
  - [Bot Owner Commands (Private Chat)](#bot-owner-commands-private-chat)
  - [User Experience & Force-Subscribe](#user-experience--force-subscribe)
- [Environment Configuration](#-environment-configuration)
- [Local Installation & Setup](#-local-installation--setup)
- [Deployment (VPS / 24/7 Hosting)](#-deployment-vps--247-hosting)
- [Required Group Permissions](#-required-group-permissions)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [License](#-license)

---

## 📖 Overview

Telegram groups frequently suffer from raid bots, affiliate links, and unsolicited advertisements. Many standard bots cannot delete messages quickly enough or are limited by Telegram's bot API restrictions.

**Anti-Promotion Shield** resolves this by operating two clients concurrently:
1. **Main Bot (Pyrogram):** Acts as the public interface—processes admin commands, serves inline button menus, enforces channel membership verification, and handles initial group invitations.
2. **Assistant Userbot (`vivbot` via Telethon):** Operates under a real Telegram user session inside the group, enabling comprehensive event interception, immediate deletion, and resilient spam countermeasures.

---

## 🏗️ System Architecture

- `config.py` — Loads and validates environment variables & credentials.
- `functions.py` — MongoDB connections, collection schemas, and auto-delete filter logic.
- `main.py` — Core bot lifecycle, Pyrogram/Telethon listeners, and Flask keep-alive server.
- `requirements.txt` — Python package dependencies.
- `.gitignore` — Prevents session files, cache, and secrets from leaking into Git.
- `README.md` — Project documentation.

---

## ⚙️ How It Works

1. **Addition to Group:** When the main bot is added as an administrator to a Telegram group, it detects the `new_chat_members` event.
2. **Assistant Provisioning:** The main bot exports or retrieves an invite link for the group and triggers the Telethon client (`vivbot`) to join automatically via `ImportChatInviteRequest`.
3. **Active Message Filtering:**
   - Incoming messages from both normal members and other bots are intercepted by both clients.
   - Group administrators and chat owners are bypassed to avoid disrupting regular group management.
   - If a message originates from a blacklisted bot or matches auto-delete criteria defined in `functions.py`, it is removed instantly.
4. **Data Persistence:** Group settings, blacklisted bots, registered users, and monitored groups are stored in MongoDB collections.

---

## 🎮 Commands & Usage

### Group Admin Commands
*These commands are executable inside groups and can only be used by group administrators.*

- `/addbot @bot_username`  
  Adds a specific bot to your group's persistent blacklist.  
  *Example:* `/addbot @spam_promo_bot`  
  *Action:* The bot saves the entry into the MongoDB `blacklist_db` for that specific group ID.

- `/delbot @bot_username`  
  Removes a previously blacklisted bot from your group's blocklist.  
  *Example:* `/delbot @spam_promo_bot`

- `/botlist`  
  Displays all bot usernames currently blacklisted in the current group.

---

### Bot Owner Commands (Private Chat)
*These commands are strictly restricted to the user whose ID matches `OWNER_ID`.*

- `/users`  
  Fetches the real-time count of unique private users who have interacted with the bot.

- `/broadcast <your message>`  
  Sends a direct announcement to every registered user in the database. Includes automated `FloodWait` handling to prevent account or bot rate limits.

- `/g_broadcast <your message>`  
  Sends an announcement across all groups tracked in the bot's database.

---

### User Experience & Force-Subscribe

When a new or existing user sends `/start` to the bot in a private chat:
1. The bot verifies if the user is a member of the required channel configured in `FORCE_SUB_CHANNEL`.
2. If the user has **not** joined, access is locked behind an inline prompt with **Join Now 🔒** and **Joined 🔑** verification buttons.
3. Once verified, the user is registered into MongoDB and presented with interactive menu options (**Add Me To Group**, **Help**, and **About**).

---

## 🔑 Environment Configuration

Create a `.env` file or export the following variables in your hosting environment:

| Variable | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `API_ID` | `int` | **Yes** | Telegram API ID from [my.telegram.org](https://my.telegram.org). |
| `API_HASH` | `str` | **Yes** | Telegram API Hash from [my.telegram.org](https://my.telegram.org). |
| `BOT_TOKEN` | `str` | **Yes** | Main bot token obtained from [@BotFather](https://t.me/BotFather). |
| `BOT_USERNAME` | `str` | **Yes** | Main bot username without the `@` symbol. |
| `DATABASE_URL` | `str` | **Yes** | MongoDB connection URI (`mongodb+srv://...`). |
| `FORCE_SUB_CHANNEL` | `str` | **Yes** | Channel username for mandatory subscription (without `@`). |
| `OWNER_ID` | `int` | **Yes** | Numerical Telegram User ID of the primary owner. |
| `PORT` | `int` | *No* | Port for the built-in Flask web server (Default: `8080`). |
| `GROUP_ID` | `int` | *No* | Primary group ID for dedicated monitoring. |
| `LOG_CHANNEL_ID` | `int` | *No* | Target channel ID for posting automated deletion and audit logs. |
| `LOGGER_BOT_TOKEN` | `str` | *No* | Bot token authorized to write to the log channel. |

---

## 💻 Local Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/vivekxn/antiPromo.git
cd antiPromo
```

### 2. Set Up Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / Git Bash)
python -m venv venv
venv\Scripts\activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
Create a `.env` file in the root directory:
```env
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
DATABASE_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
BOT_USERNAME=YourBotUsername
FORCE_SUB_CHANNEL=YourChannelUsername
OWNER_ID=123456789
PORT=8080
```

### 5. Launch the Bot
```bash
python main.py
```

> **Important Note on First Run:**  
> Telethon will ask you inside the terminal to enter your assistant phone number, confirmation code, and two-factor password (if enabled) to create the local `vivbot_session.session` file.

---

## 🚀 Deployment (VPS / 24/7 Hosting)

### Running with Systemd on a Linux VPS
To ensure the bot stays online and restarts automatically after server reboots:

1. **Create a service file:**
   ```bash
   sudo nano /etc/systemd/system/antipromo.service
   ```

2. **Add the following configuration:**
   ```ini
   [Unit]
   Description=AntiPromo Telegram Bot Service
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/antiPromo
   ExecStart=/root/antiPromo/venv/bin/python main.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload systemd, start, and enable the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start antipromo
   sudo systemctl enable antipromo
   ```

4. **View live logs:**
   ```bash
   sudo journalctl -u antipromo -f
   ```

### Web Uptime Ping (Flask Server)
The bot includes a built-in Flask web server that binds to `0.0.0.0` on your configured `PORT`. Point external ping monitors (such as **UptimeRobot**, **Better Uptime**, or **Cron-Job.org**) to your public address or container endpoint to keep free-tier cloud instances awake.

---

## 🔐 Required Group Permissions

For the system to function correctly inside groups, grant the main bot the following administrator permissions:

- **Delete Messages:** Essential to remove unauthorized promotions, links, and spam.
- **Invite Users via Link (Add Members):** Mandatory. The main bot must be able to generate or export an invite link so the Telethon assistant (`vivbot`) can automatically enter the group.

---

## ❓ Troubleshooting & FAQs

- **Q: The bot sends an alert saying "I need the Invite Users via Link admin permission". What do I do?**  
  **A:** Go to your group settings -> Administrators -> Select the bot -> Enable **"Invite Users via Link"** (or "Add Users"). Once granted, the bot will generate an invite and bring the assistant into the group.

- **Q: Why are admin messages not getting deleted?**  
  **A:** Both Pyrogram and Telethon event handlers check user admin status before applying deletion rules. Messages sent by chat administrators or owners are never touched.

- **Q: I get a `FloodWaitError` when adding the bot to a new group.**  
  **A:** Telegram rate-limits accounts that join multiple groups in rapid succession. The bot automatically intercepts this and sleeps for the designated period. Wait for the flood wait timeout to expire before adding the bot to more groups.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).