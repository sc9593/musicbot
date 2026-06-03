#!/usr/bin/env python3
""" 
🎵 Melody Stream Bot - Advanced Telegram Music Bot
Powered by JioSaavn API
Created by: @Sumanearningtrick
"""

import telebot
from telebot import types
import requests
import json
import time
import os
from datetime import datetime
import hashlib
import re

# Bot Configuration
BOT_TOKEN = "8824371818:AAEdoxOd6eu76FZb_Nyjvz-yZtSZ3M1SVuE"
ADMIN_ID = 1655373100
API_BASE_URL = "https://jiosavanapiryden.vercel.app/api"
SUPPORT_LINK = "https://t.me/EarnBazaarrr"
CHANNEL_LINK = "https://t.me/EarnBazaarrr"
CHANNEL_USERNAME = "@EarnBazaarrr"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Data storage
DATA_FILE = "bot_data.json"
bot_start_time = time.time()

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                pass
    return {
        "users": [],
        "total_downloads": 0,
        "total_searches": 0
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

data = load_data()

# User state management
user_states = {}

# Rate limiting
user_last_search = {}
RATE_LIMIT_SECONDS = 3

# Helper Functions
def add_user(user_id):
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
        return True
    return False

def is_admin(user_id):
    return user_id == ADMIN_ID

def check_rate_limit(user_id):
    now = time.time()
    if user_id in user_last_search:
        if now - user_last_search[user_id] < RATE_LIMIT_SECONDS:
            return False
    user_last_search[user_id] = now
    return True

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Force Join Check Error: {e}")
        return False

def search_songs(query, page=0, limit=15):
    try:
        url = f"{API_BASE_URL}/search/songs"
        params = {"query": query, "page": page, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None

def get_song_details(song_id):
    try:
        url = f"{API_BASE_URL}/songs/{song_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            song_data = response.json()
            if song_data.get("success") and song_data.get("data"):
                song_info = song_data["data"][0]
                download_links = song_info.get("downloadUrl", [])
                
                if download_links:
                    best_quality = download_links[-1]
                    duration_sec = song_info.get("duration", 0)
                    minutes = duration_sec // 60
                    seconds = duration_sec % 60
                    formatted_duration = f"{minutes}:{seconds:02d}"
                    
                    return {
                        "url": best_quality.get("url"),
                        "title": song_info.get("name", "Unknown"),
                        "artist": ", ".join([a.get("name", "") for a in song_info.get("artists", {}).get("primary", [])]),
                        "duration": duration_sec,
                        "duration_formatted": formatted_duration,
                        "album": song_info.get("album", {}).get("name", ""),
                        "year": song_info.get("year", "N/A")
                    }
        return None
    except Exception as e:
        print(f"Song details error: {e}")
        return None

def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("🎵 Search Music"),
        types.KeyboardButton("📊 Stats"),
        types.KeyboardButton("ℹ️ About"),
        types.KeyboardButton("📢 Share Bot"),
        types.KeyboardButton("⚙️ Help")
    ]
    keyboard.add(*buttons)
    return keyboard

def format_duration(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def format_uptime(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if secs > 0 or not parts: parts.append(f"{secs}s")
    return " ".join(parts)

# ==================== COMMAND HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id

    # Check force subscription first
    if not is_user_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)
        verify_btn = types.InlineKeyboardButton("✅ Verify", callback_data="verify_join")
        markup.add(join_btn)
        markup.add(verify_btn)

        bot.send_message(
            message.chat.id,
            "⚠️ **Bot use karne se pehle channel join karo.**\n\nNiche diye gaye channel ko join karein aur Verify button dabayein.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    # If joined, register user and show welcome screen
    first_name = message.from_user.first_name or "Music Lover"
    add_user(user_id)
    
    welcome_text = f"""🎵 WELCOME TO MELODY STREAM 🎵

✨ Hello {first_name}! ✨

Your ultimate destination for high-quality music streaming and downloads.

━━━━━━━━━━━━━━━━
🌟 WHAT I OFFER 🌟
━━━━━━━━━━━━━━━━

🎧 320KBPS Quality Audio
⚡ Instant Music Delivery
🔍 Smart Search System
📥 Unlimited Downloads

━━━━━━━━━━━━━━━━
📖 HOW TO USE 📖
━━━━━━━━━━━━━━━━

1️⃣ Tap on "🎵 Search Music"
2️⃣ Send any song/artist name
3️⃣ Choose from search results
4️⃣ Get instant high-quality audio!

━━━━━━━━━━━━━━━━
👨‍💻 Developer: @sumanearningtrick
━━━━━━━━━━━━━━━━"""
    
    bot.send_message(message.chat.id, welcome_text)
    bot.send_message(message.chat.id, "👇 Use the buttons below to get started 👇", reply_markup=create_main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    if not is_user_joined(message.from_user.id):
        return start_command(message)

    help_text = """📖 MELODY STREAM - HELP GUIDE 📖

━━━━━━━━━━━━━━━━
🎯 QUICK COMMANDS 🎯
━━━━━━━━━━━━━━━━

/start - Restart the bot
/help - Show this guide
/about - About Melody Stream
/stats - View bot statistics
/share - Share this bot

━━━━━━━━━━━━━━━━
🔍 SEARCH TIPS 🔍
━━━━━━━━━━━━━━━━

• Include artist name for better results
• Use correct spelling
• Try song with movie name

━━━━━━━━━━━━━━━━
⚡ FEATURES ⚡
━━━━━━━━━━━━━━━━

✓ High Quality Audio (320kbps)
✓ Unlimited Searches
✓ Free Forever!

━━━━━━━━━━━━━━━━
🆘 NEED HELP? Contact: @Sumanearningtrick

Enjoy your music journey! 🎧"""

    bot.send_message(message.chat.id, help_text, reply_markup=create_main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    if not is_user_joined(message.from_user.id):
        return start_command(message)

    about_text = """🎵 ABOUT MELODY STREAM 🎵

━━━━━━━━━━━━━━━━
✨ VISION ✨
━━━━━━━━━━━━━━━━

Bringing high-quality music to everyone, everywhere, completely free.

━━━━━━━━━━━━━━━━
⚙️ TECHNOLOGY ⚙️
━━━━━━━━━━━━━━━━

• Advanced Search Algorithm
• 320KBPS Audio Quality
• 24/7 Availability

━━━━━━━━━━━━━━━━
👨‍💻 DEVELOPER 👨‍💻
━━━━━━━━━━━━━━━━

Name: suman chowdhury
Contact: @Sumanearningtrick

━━━━━━━━━━━━━━━━
📊 BOT STATS 📊
━━━━━━━━━━━━━━━━

Use /stats to view bot statistics

Keep vibing with Melody Stream! 🎧"""

    bot.send_message(message.chat.id, about_text, reply_markup=create_main_keyboard())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if not is_user_joined(message.from_user.id):
        return start_command(message)

    user_id = message.from_user.id
    total_users = len(data["users"])
    total_searches = data.get("total_searches", 0)
    total_downloads = data.get("total_downloads", 0)
    uptime = time.time() - bot_start_time
    uptime_str = format_uptime(uptime)
    
    stats_text = f"""📊 MELODY STREAM STATISTICS 📊

━━━━━━━━━━━━━━━━
📈 USAGE METRICS 📈
━━━━━━━━━━━━━━━━

👥 Total Users: {total_users:,}
🔍 Total Searches: {total_searches:,}
📥 Total Downloads: {total_downloads:,}
⏱️ Bot Uptime: {uptime_str}

━━━━━━━━━━━━━━━━
⚡ PERFORMANCE ⚡
━━━━━━━━━━━━━━━━

💾 Database: Active
🌐 API Status: Online
🎵 Music Source: JioSaavn
📦 Quality: Up to 320kbps

━━━━━━━━━━━━━━━━

Thanks for using Melody Stream! 🎧

— @Sumanearningtrick"""
    
    if is_admin(user_id):
        stats_text += f"""

━━━━━━━━━━━━━━━━
👑 ADMIN INFO 👑
━━━━━━━━━━━━━━━━

👤 Admin ID: {ADMIN_ID}
✅ Status: Active"""
    
    bot.send_message(message.chat.id, stats_text, reply_markup=create_main_keyboard())

@bot.message_handler(commands=['share'])
def share_command(message):
    if not is_user_joined(message.from_user.id):
        return start_command(message)

    bot_username = bot.get_me().username
    share_text = f"🎵 Discover Melody Stream - The Ultimate Music Bot!\n\n✅ Free High-Quality Music\n✅ Instant Downloads\n✅ Unlimited Searches\n\nTry it now: t.me/{bot_username}\n\nCreated by @vishalcodeverse"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    tg_share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}&text={requests.utils.quote(share_text)}"
    wa_share_url = f"https://wa.me/?text={requests.utils.quote(share_text)}"
    
    tg_btn = types.InlineKeyboardButton("📱 Telegram", url=tg_share_url)
    wa_btn = types.InlineKeyboardButton("💬 WhatsApp", url=wa_share_url)
    
    markup.add(tg_btn, wa_btn)
    bot.send_message(message.chat.id, "📢 SHARE MELODY STREAM\n\nShare with friends 👇", reply_markup=markup)

# ==================== BUTTON HANDLERS ====================

@bot.message_handler(func=lambda message: message.text == "🎵 Search Music")
def search_music_button(message):
    if not is_user_joined(message.from_user.id):
        return start_command(message)

    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_song"
    
    search_prompt = """🎵 SEARCH FOR MUSIC 🎵

━━━━━━━━━━━━━━━━
✨ SEARCH TIPS ✨
━━━━━━━━━━━━━━━━

🎤 By Artist: "Arijit Singh"
🎧 By Song: "Shape of You"
🎬 By Movie: "Animal songs"

━━━━━━━━━━━━━━━━
📝 EXAMPLES 📝
━━━━━━━━━━━━━━━━

→ Believer
→ Tere Bina Na Gujara
→ Pal Pal by Talwinder

━━━━━━━━━━━━━━━━

Type your search query below: 👇

Send /cancel to cancel ❌"""

    bot.send_message(message.chat.id, search_prompt)

@bot.message_handler(func=lambda message: message.text == "📊 Stats")
def stats_button_handler(message):
    stats_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ About")
def about_button_handler(message):
    about_command(message)

@bot.message_handler(func=lambda message: message.text == "📢 Share Bot")
def share_button_handler(message):
    share_command(message)

@bot.message_handler(func=lambda message: message.text == "⚙️ Help")
def help_button_handler(message):
    help_command(message)

# ==================== ADMIN COMMANDS ====================

@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Access Denied!\n\nYou don't have permission to access admin panel.")
        return
    
    admin_text = f"""👑 ADMIN PANEL 👑

━━━━━━━━━━━━━━━━
📋 COMMANDS 📋
━━━━━━━━━━━━━━━━

/stats - View bot statistics
/broadcast - Send message to users
/ping - Check bot status
/backup - Download user backup
/announce - Make announcement

━━━━━━━━━━━━━━━━
📊 QUICK INFO 📊
━━━━━━━━━━━━━━━━

👤 Admin ID: {ADMIN_ID}
📁 Total Users: {len(data["users"])}
✅ Status: Active

━━━━━━━━━━━━━━━━

— @EarnBazaarrr"""
    
    bot.send_message(message.chat.id, admin_text)

@bot.message_handler(commands=['ping'])
def ping_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    start = time.time()
    msg = bot.send_message(message.chat.id, "🏓 Pinging...")
    end = time.time()
    
    response_time = round((end - start) * 1000, 2)
    uptime = time.time() - bot_start_time
    
    ping_text = f"""🏓 PONG!

━━━━━━━━━━━━━━━━
⚡ RESPONSE TIME ⚡
━━━━━━━━━━━━━━━━

📡 Latency: {response_time}ms
⏱️ Uptime: {format_uptime(uptime)}
✅ Status: Online & Healthy

— @sumanearningtrick"""
    
    bot.edit_message_text(ping_text, message.chat.id, msg.message_id)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(message.chat.id, "📢 BROADCAST MESSAGE\n\nSend the message you want to broadcast to all users.\n\nSend /cancel to cancel.")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ Broadcast cancelled.")
        return
    
    broadcast_text = message.text
    status_msg = bot.send_message(message.chat.id, "📤 Broadcasting message...\n\n⏳ Please wait...")
    
    success = 0
    failed = 0
    
    for u_id in data["users"]:
        try:
            bot.send_message(u_id, f"📢 ANNOUNCEMENT\n\n━━━━━━━━━━━━━━━━\n\n{broadcast_text}\n\n━━━━━━━━━━━━━━━━\n\n— @vishalcodeverse")
            success += 1
            time.sleep(0.05)
        except Exception as e:
            failed += 1
            print(f"Failed to send to {u_id}: {e}")
    
    result_text = f"""✅ BROADCAST COMPLETE ✅

━━━━━━━━━━━━━━━━
📊 STATISTICS 📊
━━━━━━━━━━━━━━━━

✅ Successful: {success}
❌ Failed: {failed}
👥 Total Users: {len(data["users"])}

— @sumanearningtrick"""
    
    bot.edit_message_text(result_text, message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['backup'])
def backup_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    try:
        backup_data = {
            "total_users": len(data["users"]),
            "users": data["users"],
            "total_searches": data.get("total_searches", 0),
            "total_downloads": data.get("total_downloads", 0),
            "backup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        with open(backup_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"💾 USER BACKUP\n\n👥 Total Users: {len(data['users'])}\n📅 Date: {backup_data['backup_date']}")
        
        os.remove(backup_file)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Backup Failed!\n\nError: {str(e)}")

@bot.message_handler(commands=['announce'])
def announce_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(message.chat.id, "📢 MAKE AN ANNOUNCEMENT\n\nSend your announcement message. It will be pinned!\n\nSend /cancel to cancel.")
    bot.register_next_step_handler(msg, process_announcement)

def process_announcement(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ Announcement cancelled.")
        return
    
    announce_text = message.text
    sent_msg = bot.send_message(message.chat.id, f"📢 ANNOUNCEMENT\n\n━━━━━━━━━━━━━━━━\n\n{announce_text}\n\n━━━━━━━━━━━━━━━━\n\n— @vishalcodeverse")
    
    try:
        bot.pin_chat_message(message.chat.id, sent_msg.message_id)
    except Exception as e:
        print(f"Failed to pin message: {e}")
    
    bot.send_message(message.chat.id, "✅ Announcement posted and pinned!")

# ==================== TEXT HANDLER ====================

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    
    # Global check for Force Subscription on standard interactions
    if not is_user_joined(user_id):
        return start_command(message)

    # Handle cancel
    if message.text == '/cancel' and user_id in user_states:
        del user_states[user_id]
        bot.send_message(message.chat.id, "❌ Search cancelled", reply_markup=create_main_keyboard())
        return
    
    if message.text.startswith('/'):
        return
    
    # Handle music search text input
    if user_id in user_states and user_states.get(user_id) == "waiting_for_song":
        del user_states[user_id]
        
        if not check_rate_limit(user_id):
            bot.send_message(message.chat.id, "⏳ Please wait a few seconds before searching again!")
            return
        
        search_query = message.text.strip()
        if len(search_query) < 2:
            bot.send_message(message.chat.id, "❌ Please enter a valid song name (at least 2 characters)")
            return
        
        searching_msg = bot.send_message(message.chat.id, f"🎵 Searching: {search_query}\n\n⏳ Scanning music database...")
        results = search_songs(search_query, page=0, limit=15)
        
        if not results or not results.get("success"):
            bot.edit_message_text("❌ No Results Found!\n\nPlease try different spelling or add artist name.", message.chat.id, searching_msg.message_id)
            return
        
        songs = results.get("data", {}).get("results", [])
        if not songs:
            bot.edit_message_text("❌ No songs found!\n\n💡 Tips: Check spelling or try fewer words.", message.chat.id, searching_msg.message_id)
            return
        
        data["total_searches"] = data.get("total_searches", 0) + 1
        save_data(data)
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for idx, song in enumerate(songs[:15], 1):
            song_name = song.get("name", "Unknown")
            artists = song.get("artists", {}).get("primary", [])
            artist_names = ", ".join([a.get("name", "") for a in artists[:2]])
            duration = song.get("duration", 0)
            duration_str = format_duration(duration)
            
            if artist_names:
                button_text = f"{idx}. {song_name[:35]} - {artist_names[:25]} [{duration_str}]"
            else:
                button_text = f"{idx}. {song_name[:45]} [{duration_str}]"
            
            callback_data = f"song_{song.get('id')}"
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
        
        bot.edit_message_text(f"🎵 SEARCH RESULTS\n\n🔍 For: {search_query}\n📊 Found: {len(songs)} songs\n\n✨ Select a song to download:", message.chat.id, searching_msg.message_id, reply_markup=markup)
        
        nav_markup = types.InlineKeyboardMarkup(row_width=2)
        nav_markup.add(types.InlineKeyboardButton("🔄 New Search", callback_data="new_search"), types.InlineKeyboardButton("📊 Stats", callback_data="quick_stats"))
        bot.send_message(message.chat.id, "👇 Need more options? 👇", reply_markup=nav_markup)
        return
    
    # Invalid message fallback
    if message.text not in ["🎵 Search Music", "📊 Stats", "ℹ️ About", "📢 Share Bot", "⚙️ Help"]:
        bot.send_message(message.chat.id, "❌ Invalid Command\n\nUse the buttons below or send /help for assistance 👇", reply_markup=create_main_keyboard())

# ==================== CALLBACK HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join_callback(call):
    if is_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified Successfully")
        
        # Clean up validation block message
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
            
        bot.send_message(
            call.message.chat.id,
            "🎉 **Verification Complete!**\n\nAb aap saare features fully use kar sakte ho.",
            reply_markup=create_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Pehle Channel Join Karo",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('song_'))
def song_callback(call):
    if not is_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "⚠️ Pehle Channel Join Karo!", show_alert=True)
        return
        
    song_id = call.data.replace('song_', '')
    bot.answer_callback_query(call.id, "🔄 Fetching your song...")
    processing_msg = bot.send_message(call.message.chat.id, "🎵 PROCESSING YOUR REQUEST\n\n⏳ Fetching high-quality audio...")
    
    try:
        song_details = get_song_details(song_id)
        if not song_details or not song_details.get("url"):
            bot.edit_message_text("❌ Download Failed!\n\n⚠️ Unable to fetch download link. Please try again.", call.message.chat.id, processing_msg.message_id)
            return
        
        download_url = song_details["url"]
        title = song_details["title"]
        artist = song_details["artist"] or "Unknown Artist"
        duration = song_details["duration"]
        duration_formatted = song_details.get("duration_formatted", format_duration(duration))
        album = song_details.get("album", "Single")
        year = song_details.get("year", "N/A")
        
        bot.edit_message_text(f"🎵 DOWNLOADING\n\n📀 Song: {title}\n🎤 Artist: {artist}\n⏱️ Duration: {duration_formatted}\n\n⏳ Preparing your file...", call.message.chat.id, processing_msg.message_id)
        audio_response = requests.get(download_url, timeout=45)
        
        if audio_response.status_code != 200:
            bot.edit_message_text("❌ Download Failed!\n\n⚠️ Server error. Please try again.", call.message.chat.id, processing_msg.message_id)
            return
        
        temp_filename = f"temp_{song_id}_{hashlib.md5(title.encode()).hexdigest()[:8]}.mp3"
        with open(temp_filename, 'wb') as f:
            f.write(audio_response.content)
        
        bot.edit_message_text(f"🎵 SENDING YOUR MUSIC\n\n📀 {title}\n🎤 {artist}\n\n⏳ Uploading to Telegram...", call.message.chat.id, processing_msg.message_id)
        
        caption = f"""🎵 {title} 🎵

━━━━━━━━━━━━━━━━
✨ TRACK DETAILS ✨
━━━━━━━━━━━━━━━━

🎤 Artist: {artist}
⏱️ Duration: {duration_formatted}
💿 Album: {album}
📅 Year: {year}
📊 Quality: 320kbps MP3

━━━━━━━━━━━━━━━━
👨‍💻 Developer: @EarnBazaarrr

🎧 Keep vibing with Melody Stream!"""
        
        with open(temp_filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=title[:60], performer=artist[:60], duration=duration, caption=caption)
        
        try:
            bot.delete_message(call.message.chat.id, processing_msg.message_id)
        except:
            pass
        try:
            os.remove(temp_filename)
        except:
            pass
        
        data["total_downloads"] = data.get("total_downloads", 0) + 1
        save_data(data)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎵 Search Again", callback_data="new_search"), types.InlineKeyboardButton("📢 Share Bot", callback_data="share_bot"))
        bot.send_message(call.message.chat.id, "✅ Song Sent Successfully!\n\nWant more music? Use the buttons below 👇", reply_markup=markup)
        
    except Exception as e:
        print(f"Error in song_callback: {e}")
        try:
            bot.edit_message_text(f"❌ Error Occurred!\n\nPlease try again later.", call.message.chat.id, processing_msg.message_id)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data == "new_search")
def new_search_callback(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_for_song"
    bot.answer_callback_query(call.id, "🔍 Ready to search!")
    bot.send_message(call.message.chat.id, "🎵 Enter your search query:\n\nSend any song or artist name! 🎧\n\nSend /cancel to cancel")

@bot.callback_query_handler(func=lambda call: call.data == "quick_search")
def quick_search_callback(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_for_song"
    bot.answer_callback_query(call.id, "🔍 Type song name to search!")
    bot.send_message(call.message.chat.id, "🎵 What would you like to listen to?\n\nSend song name or artist name!\n\nExample: Believer Imagine Dragons\n\nSend /cancel to cancel")

@bot.callback_query_handler(func=lambda call: call.data == "quick_stats")
def quick_stats_callback(call):
    bot.answer_callback_query(call.id, "📊 Fetching statistics...")
    stats_command(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "share_bot")
def share_bot_callback(call):
    bot.answer_callback_query(call.id, "📢 Sharing options...")
    share_command(call.message)

# ==================== MAIN FUNCTION & DUMMY SERVER ====================
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Melody Stream Bot is Alive and Running!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def main():
    print("=" * 50)
    print("🎵 MELODY STREAM BOT - STARTING UP 🎵")
    print("=" * 50)
    print(f"👑 Developer: @sumanearningtrick")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"📊 Total Users: {len(data['users'])}")
    print(f"🔍 Total Searches: {data.get('total_searches', 0)}")
    print(f"📥 Total Downloads: {data.get('total_downloads', 0)}")
    print(f"⏱️ Bot Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print("✅ Bot is running successfully!")
    print("✅ Admin panel command: /admin")
    print("=" * 50)
    
    # 1. Start Web Server in background thread (To keep Render happy)
    threading.Thread(target=run_server).start()
    
    # 2. Start Bot
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ Polling error: {e}")
            print("🔄 Restarting bot in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
