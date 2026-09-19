import os
import asyncio
import threading
from flask import Flask
import discord

# --- Web Server หลอก Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Discord Bot ---
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

client = discord.Client(intents=intents)

# 📌 ใส่ ID ห้อง "พูดคุยรุ่นใหญ่" ตรงนี้
VOICE_CHANNEL_ID = 1512748513492902132

async def keep_voice_alive():
    await client.wait_until_ready()
    print('==========================================')
    print(f'[ONLINE] บอท {client.user} ล็อกอินสำเร็จแล้ว!')
    print('==========================================')
    await client.change_presence(activity=discord.Game(name="สิงห้องพูดคุยรุ่นใหญ่ 24 ชม. 🟢"))
    
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                try:
                    channel = await client.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    print(f'[ERROR] หาห้องไม่เจอ: {e}')

            if channel:
                # ถ้าบอทยังไม่เข้าห้อง ให้สั่งเข้าห้องทันที
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}...')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[SUCCESS] เข้าห้องเสียงสำเร็จแล้ว!')
            else:
                print(f'[ERROR] หาห้อง ID {VOICE_CHANNEL_ID} ไม่พบ')
        except Exception as e:
            print(f'[CRITICAL ERROR] เกิดข้อผิดพลาด: {e}')
        
        await asyncio.sleep(5)

@client.event
async def on_ready():
    # เมื่อบอทพร้อม สั่งเริ่มรันลูปเฝ้าห้องเสียงทันที
    client.loop.create_task(keep_voice_alive())

if __name__ == '__main__':
    # รัน Web Server แยกใน Background
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # รัน Discord Bot
    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
