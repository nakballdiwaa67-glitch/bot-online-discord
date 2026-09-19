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

class VoiceBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_connecting = False

    async def setup_hook(self):
        # สร้าง Loop เช็กความเรียบร้อยเมื่อบอทเริ่มทำงาน
        self.loop.create_task(self.background_check())

    async def connect_voice_channel(self):
        if self.is_connecting:
            return
        
        self.is_connecting = True
        try:
            channel = self.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                try:
                    channel = await self.fetch_channel(VOICE_CHANNEL_ID)
                except Exception:
                    pass

            if channel:
                # ถ้าอยู่ในห้องเสียงเดิมและเชื่อมต่อสมบูรณ์แล้ว ไม่ต้องทำอะไร
                if self.voice_clients:
                    vc = self.voice_clients[0]
                    if vc.channel.id == VOICE_CHANNEL_ID and vc.is_connected():
                        self.is_connecting = False
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
            self.is_connecting = False

    async def background_check(self):
        await self.wait_until_ready()
        while not self.is_closed():
            # เช็กความเสถียรทุก 30 วินาที ไม่ถี่เกินไปจนตัดสายเอง
            if not self.voice_clients or not self.voice_clients[0].is_connected():
                await self.connect_voice_channel()
            await asyncio.sleep(30)

client = VoiceBot(intents=intents)

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์แล้ว!', flush=True)
    try:
        await client.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
    except Exception:
        pass
    
    await client.connect_voice_channel()

@client.event
async def on_voice_state_update(member, before, after):
    # ถ้าบอทโดนเตะหรือสายหลุด ให้สั่งเชื่อมต่อใหม่
    if member.id == client.user.id:
        if after.channel is None or after.channel.id != VOICE_CHANNEL_ID:
            await asyncio.sleep(3)
            await client.connect_voice_channel()

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN!', flush=True)
