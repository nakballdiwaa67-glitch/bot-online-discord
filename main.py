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
VOICE_CHANNEL_ID = 1512748513492992132

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

client = discord.Client(intents=intents)

is_connecting = False

async def connect_voice_channel():
    global is_connecting
    if is_connecting:
        return
    
    is_connecting = True
    try:
        channel = client.get_channel(VOICE_CHANNEL_ID)
        if channel is None:
            try:
                channel = await client.fetch_channel(VOICE_CHANNEL_ID)
            except Exception:
                pass

        if channel:
            # เช็กว่าถ้าอยู่ในห้องเสียงเดิมอยู่แล้ว และเชื่อมต่อสมบูรณ์ ไม่ต้องทำอะไร
            if client.voice_clients:
                vc = client.voice_clients[0]
                if vc.channel.id == VOICE_CHANNEL_ID and vc.is_connected():
                    is_connecting = False
                    return
                else:
                    await vc.disconnect(force=True)
                    await asyncio.sleep(1)

            print(f'[VOICE] กำลังเข้าห้องเสียง: {channel.name}...', flush=True)
            await channel.connect(reconnect=True, self_deaf=True, timeout=15.0)
            print(f'[SUCCESS] เชื่อมต่อและสิงห้องเรียบร้อย!', flush=True)
    except Exception as e:
        print(f'[ERROR] เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}', flush=True)
    finally:
        is_connecting = False

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์แล้ว!', flush=True)
    try:
        await client.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
    except Exception:
        pass
    
    # พยายามเข้าห้องเสียงเมื่อออนไลน์
    await connect_voice_channel()

@client.event
async def on_voice_state_update(member, before, after):
    # ถ้าตัวบอทเองโดนเตะหลุด หรือถูกย้ายห้อง ให้พยายามกลับเข้าห้องเดิม
    if member.id == client.user.id:
        if after.channel is None or after.channel.id != VOICE_CHANNEL_ID:
            await asyncio.sleep(3)
            await connect_voice_channel()

async def background_check():
    await client.wait_until_ready()
    while not client.is_closed():
        # เช็กความถูกต้องทุกๆ 30 วินาทีพอ ไม่ต้องเช็กถี่เพื่อป้องกันลูปตีกัน
        if not client.voice_clients or not client.voice_clients[0].is_connected():
            await connect_voice_channel()
        await asyncio.sleep(30)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        # เริ่มต้น Background Task เช็กความเสถียร
        client.loop.create_task(background_check())
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN!', flush=True)
