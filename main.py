import os
import asyncio
import threading
from flask import Flask
import discord

# --- 1. Web Server หลอก Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 2. ตั้งค่า Discord Bot ---
# 📌 ID ห้อง "ทำงานแอดมิน"
VOICE_CHANNEL_ID = 1512748513492992132

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

client = discord.Client(intents=intents)

async def keep_voice_alive():
    await client.wait_until_ready()
    print(f'[ONLINE] บอท {client.user} ล็อกอินสำเร็จแล้ว!', flush=True)
    
    try:
        await client.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
    except Exception:
        pass

    while not client.is_closed():
        try:
            # เช็กว่าเชื่อมต่ออยู่นิ่งๆ แล้วหรือยัง
            if client.voice_clients and client.voice_clients[0].is_connected():
                await asyncio.sleep(15)
                continue

            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                try:
                    channel = await client.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    print(f'[ERROR] หาห้อง ID {VOICE_CHANNEL_ID} ไม่เจอ: {e}', flush=True)

            if channel:
                print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}...', flush=True)
                
                # ล้างการเชื่อมต่อเก่าที่ค้างอยู่
                if client.voice_clients:
                    try:
                        await client.voice_clients[0].disconnect(force=True)
                    except Exception:
                        pass
                    await asyncio.sleep(2)

                # เชื่อมต่อเข้าห้องเสียงพร้อมกำหนด timeout ป้องกันการค้าง
                await channel.connect(reconnect=True, self_deaf=True, timeout=30.0)
                print(f'[SUCCESS] เข้าห้องเสียงเรียบร้อย นั่งยาวๆ ได้เลย!', flush=True)
                await asyncio.sleep(10)
            else:
                print(f'[ERROR] หาห้องเสียงไม่พบ', flush=True)

        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาดระหว่างต่อสาย: {e}', flush=True)
        
        await asyncio.sleep(5)

@client.event
async def on_ready():
    client.loop.create_task(keep_voice_alive())

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN ใน Environment Variables!', flush=True)
