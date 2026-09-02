<div align="center">

# 🛡️ Anti-Promotion Shield Bot

**A powerful, dual-engine Telegram spam and anti-promotion management bot.**  
Built using **Pyrogram** for handling bot interactions and commands, paired with a **Telethon** userbot assistant for group joining and administrative operations.

---

</div>

## 📌 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [Commands](#-commands)
  - [Group Commands](#group-commands)
  - [Owner Commands (Private)](#owner-commands-private)
- [Environment Variables](#-environment-variables)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Bot](#running-the-bot)
- [Deployment](#-deployment)
- [Required Permissions](#-required-permissions)
- [License](#-license)

---

## 📖 About the Project

Managing public and private Telegram communities can be challenging due to automated spam bots, unauthorized cross-promotional links, and scam attempts. 

**Anti-Promotion Shield** provides automated protection by:
1. Monitoring messages in protected groups in real-time.
2. Checking against blacklisted bots and unauthorized promotional material.
3. Automatically bringing an assistant userbot (`vivbot`) via invite links to handle privileged actions if required.
4. Enforcing force-subscription to updates channels for private command access.

---

## ✨ Key Features

- ⚡ **Dual Engine:** Combines **Pyrogram Client** (fast webhook/polling bot interactions) and **Telethon Client** (userbot actions).
- 🧹 **Auto Message Deletion:** Cleans up promotional text, blacklisted bot broadcasts, and spam instantly.
- 🚫 **Dynamic Bot Blacklist:** Group administrators can add, remove, and review custom blacklisted bot usernames on a per-group basis.
- 🔗 **Automatic Assistant Integration:** When the main bot is added to a group, it exports an invite link and automatically joins the userbot assistant into the group.
- 🔒 **Force-Subscribe Gatekeeper:** Ensures users subscribe to your updates channel before accessing private menu options.
- 📢 **Broadcasting Tools:** Owner-only tools to broadcast announcements to all users or all tracked groups with built-in flood wait handlers.
- 🌐 **Integrated Flask Server:** Built-in web server to satisfy uptime monitors (e.g., UptimeRobot, Render, Koyeb).

---

## 🛠️ Project Architecture

```text
├── config.py         # Environment configuration and credential loader
├── functions.py      # Database handlers (MongoDB) & auto-delete processing logic
├── main.py           # Application entry point, Pyrogram & Telethon event listeners
├── requirements.txt  # Project library dependencies
└── README.md         # Project documentation