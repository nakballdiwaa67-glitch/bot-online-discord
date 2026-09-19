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
    except Exception as e:
        pass

    while not client.is_closed():
        try:
            # 1. เช็กว่าบอทเชื่อมต่อห้องเสียงอยู่นิ่งๆ แล้วหรือยัง
            if client.voice_clients and client.voice_clients[0].is_connected():
                # ถ้าอยู่ในห้องเสียงดีอยู่แล้ว ให้หน่วงเวลา 15 วินาที แล้ววนลูปเช็กใหม่ (ไม่สั่ง connect ซ้ำ)
                await asyncio.sleep(15)
                continue

            # 2. ถ้ายังไม่ได้เข้า หรือสายหลุดจริงๆ ให้ดึงห้องเสียง
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                try:
                    channel = await client.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    print(f'[ERROR] หาห้อง ID {VOICE_CHANNEL_ID} ไม่เจอ: {e}', flush=True)

            if channel:
                print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}...', flush=True)
                
                # ตัดสายค้างเก่าออกก่อนเพื่อความสะอาด
                if client.voice_clients:
                    await client.voice_clients[0].disconnect(force=True)
                    await asyncio.sleep(2)

                # สั่งเชื่อมต่อเข้าห้องเสียง
                await channel.connect(reconnect=True, self_deaf=True)
                print(f'[SUCCESS] เข้าห้องเสียงและล็อกสถานะเรียบร้อย!', flush=True)
                
                # รอให้ระบบเชื่อมต่อ Voice Gateway เสถียรก่อน 10 วินาที
                await asyncio.sleep(10)
            else:
                print(f'[ERROR] หาห้องเสียงไม่พบ', flush=True)

        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาดในห้องเสียง: {e}', flush=True)
        
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
