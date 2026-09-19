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

# --- 2. Discord Bot Class ---
# 📌 ID ห้องเสียง "พูดคุยรุ่นใหญ่"
VOICE_CHANNEL_ID = 1512748513492902132

class AdminVoiceBot(discord.Client):
    async def setup_hook(self):
        self.loop.create_task(self.keep_voice_alive())

    async def keep_voice_alive(self):
        await self.wait_until_ready()
        print(f'==========================================')
        print(f'[ONLINE] บอท {self.user} ล็อกอินสำเร็จแล้ว!')
        print(f'==========================================')
        await self.change_presence(activity=discord.Game(name="สิงห้องพูดคุยรุ่นใหญ่ 24 ชม. 🟢"))
        
        while not self.is_closed():
            try:
                channel = self.get_channel(VOICE_CHANNEL_ID)
                if channel is None:
                    print(f'[CHECK] กำลังค้นหาห้อง ID: {VOICE_CHANNEL_ID} ผ่านการ Fetch...')
                    try:
                        channel = await self.fetch_channel(VOICE_CHANNEL_ID)
                    except Exception as fetch_error:
                        print(f'[ERROR] หาห้องไม่เจอจริงๆ! สาเหตุ: {fetch_error}')

                if channel:
                    print(f'[FOUND] เจอห้องเสียงชื่อ: "{channel.name}" ในเซิร์ฟเวอร์ "{channel.guild.name}"')
                    
                    # ถ้ายังไม่เชื่อมต่อ ให้กดเข้าห้อง
                    if not self.voice_clients or not self.voice_clients[0].is_connected():
                        print(f'[VOICE] กำลังส่งคำสั่ง connect() เข้าห้อง {channel.name}...')
                        
                        # บังคับตัดสายเดิมก่อนเชื่อมต่อใหม่เพื่อความแน่นอน
                        if self.voice_clients:
                            await self.voice_clients[0].disconnect(force=True)
                            
                        vc = await channel.connect(reconnect=True, self_deaf=True)
                        print(f'[SUCCESS] เชื่อมต่อเข้าห้องเสียงสำเร็จแล้ว! (Session ID: {vc.session_id})')
                    else:
                        print(f'[STATUS] บอทอยู่ในห้องเสียงอยู่แล้วปกติ')
            except Exception as e:
                print(f'[CRITICAL ERROR] เกิดข้อผิดพลาดระหว่างเข้าห้องเสียง: {e}')
            
            # ตรวจเช็กสถานะทุกๆ 10 วินาที
            await asyncio.sleep(10)

intents = discord.Intents.default()
# เปิด intents ให้ครบถ้วน
intents.guilds = True
intents.voice_states = True

client = AdminVoiceBot(intents=intents)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
