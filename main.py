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

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 📌 วาง ID ห้อง "ทำงานแอดมิน" ที่ก๊อปปี้มาตรงนี้
VOICE_CHANNEL_ID = 1512748513492992132

async def force_connect_voice():
    await client.wait_until_ready()
    print(f'[ONLINE] บอท {client.user} ล็อกอินสำเร็จแล้ว!')
    
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                # ถ้ายังไม่เชื่อมต่อ ให้ต่อสายเข้าห้องทันที
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังกดเข้าห้อง: {channel.name}')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เข้าห้องสำเร็จ!')
            else:
                print(f'[ERROR] หาห้อง ID: {VOICE_CHANNEL_ID} ไม่เจอ! ตรวจสอบ ID หรือสิทธิ์บอท')
        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาด: {e}')
        
        await asyncio.sleep(10)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))

if __name__ == '__main__':
    # รัน Web Server แยกใน background
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # รัน Task เฝ้าห้องเสียงคู่กับบอท
    client.loop.create_task(force_connect_voice())

    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
