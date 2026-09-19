import os
import asyncio
import threading
from flask import Flask
import discord

# --- 1. ระบบ Web Server (Flask) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    # ปิด reloader และ debug เพื่อไม่ให้รบกวน Thread หลัก
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 2. ตั้งค่า Discord Bot ---
# 📌 ID ห้อง "พูดคุยรุ่นใหญ่"
VOICE_CHANNEL_ID = 1512748513492902132

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

client = discord.Client(intents=intents)

async def keep_voice_alive():
    await client.wait_until_ready()
    print(f'[ONLINE] บอท {client.user} ล็อกอินสำเร็จแล้ว!', flush=True)
    
    try:
        await client.change_presence(activity=discord.Game(name="สิงห้องพูดคุยรุ่นใหญ่ 24 ชม. 🟢"))
    except Exception as e:
        print(f'[WARNING] ตั้งค่า Status ไม่สำเร็จ: {e}', flush=True)

    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                try:
                    channel = await client.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    print(f'[ERROR] หาห้อง ID {VOICE_CHANNEL_ID} ไม่เจอ: {e}', flush=True)

            if channel:
                # ถ้ายังไม่มี Voice Client หรือไม่ได้เชื่อมต่อ ให้กดเข้าห้องทันที
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}...', flush=True)
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[SUCCESS] เข้าห้องเสียงเรียบร้อยแล้ว!', flush=True)
            else:
                print(f'[ERROR] หาห้องเสียงไม่พบ', flush=True)
        except Exception as e:
            print(f'[CRITICAL ERROR] เกิดข้อผิดพลาดในห้องเสียง: {e}', flush=True)
        
        await asyncio.sleep(5)

@client.event
async def on_ready():
    # เรียกทำงาน Task เฝ้าห้องเสียงทันทีที่บอทพร้อม
    client.loop.create_task(keep_voice_alive())

# --- 3. จุดเริ่มต้นการรันโปรแกรม ---
if __name__ == '__main__':
    # รัน Web Server แยก Thread ก่อน
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    # รัน Discord Bot
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN ใน Environment Variables!', flush=True)
