import os
import asyncio
import threading
from flask import Flask
import discord

# --- 1. Web Server หลอก Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is active 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. Discord Bot ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 📌 ระบุ ID ของห้อง "ทำงานแอดมิน" (ตรวจเช็กตัวเลขให้ถูกต้อง)
VOICE_CHANNEL_ID = 1512748513492902132

async def keep_voice_alive():
    await client.wait_until_ready()
    print(f'[ONLINE] บอท {client.user} ออนไลน์แล้ว! กำลังเริ่มทำงานระบบห้องเสียง...')
    await client.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
    
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                # เช็กว่าบอทเชื่อมต่ออยู่หรือไม่ ถ้ายังไม่เข้าหรือสายหลุด ให้สั่งเชื่อมต่อ
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังดึงบอทเข้าห้อง: {channel.name}')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] ดึงบอทเข้าห้องสำเร็จ!')
            else:
                print(f'[ERROR] หาห้อง ID: {VOICE_CHANNEL_ID} ไม่เจอ ตรวจสอบ ID หรือสิทธิ์บอทอีกครั้ง')
        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาดในห้องเสียง: {e}')
        
        # วนลูปตรวจเช็กทุกๆ 5 วินาที
        await asyncio.sleep(5)

@client.event
async def on_ready():
    # เรียกทำงานTask ห้องเสียงเมื่อพร้อม
    client.loop.create_task(keep_voice_alive())

if __name__ == '__main__':
    # รัน Web Server แยกใน Background Thread
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # รัน Discord Bot
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN ใน Environment Variables!')
