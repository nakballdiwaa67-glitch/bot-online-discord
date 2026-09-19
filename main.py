import os
import asyncio
import threading
from flask import Flask
import discord

# --- 1. สร้าง Web Server หลอก Render ไม่ให้ Kill บอท ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_flask():
    # Render จะส่ง PORT มาให้ใน Environment Variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. ตั้งค่า Discord Bot ---
intents = discord.Intents.all()
client = discord.Client(intents=intents)

VOICE_CHANNEL_ID = 1512748513492902132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="สิงห้องเสียง 24 ชม. 🟢"))
    client.loop.create_task(keep_voice_alive())

async def keep_voice_alive():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            else:
                print(f'[ERROR] หาห้องเสียง ID: {VOICE_CHANNEL_ID} ไม่เจอ')
        except Exception as e:
            print(f'[ERROR] Voice connection error: {e}')
        
        await asyncio.sleep(10)

# --- 3. รันทั้ง Web Server และ Bot พร้อมกัน ---
if __name__ == '__main__':
    # รัน Flask แยกใน Thread สำรอง
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # รัน Discord Bot
    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
