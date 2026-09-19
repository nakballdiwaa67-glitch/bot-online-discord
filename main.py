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

class AdminVoiceBot(discord.Client):
    async def setup_hook(self):
        # สร้าง Background Task แยกเด็ดขาดตั้งแต่นาทีแรกที่เริ่มรัน
        self.loop.create_task(self.keep_voice_alive())

    async def keep_voice_alive(self):
        await self.wait_until_ready()
        print(f'[ONLINE] บอท {self.user} ล็อกอินสำเร็จแล้ว!', flush=True)
        
        try:
            await self.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
        except Exception:
            pass

        while not self.is_closed():
            try:
                # ถ้าเข้าห้องเสียงอยู่แล้ว และสถานะปกติ ให้ข้ามไปรอนิ่งๆ 20 วินาที
                if self.voice_clients and self.voice_clients[0].is_connected():
                    await asyncio.sleep(20)
                    continue

                channel = self.get_channel(VOICE_CHANNEL_ID)
                if channel is None:
                    try:
                        channel = await self.fetch_channel(VOICE_CHANNEL_ID)
                    except Exception as e:
                        print(f'[ERROR] หาห้องไม่เจอ: {e}', flush=True)

                if channel:
                    print(f'[VOICE] กำลังเข้าห้อง: {channel.name}...', flush=True)
                    
                    # ล้างสายเก่าทิ้ง
                    if self.voice_clients:
                        try:
                            await self.voice_clients[0].disconnect(force=True)
                        except Exception:
                            pass
                        await asyncio.sleep(2)

                    # เชื่อมต่อแบบปิด reconnect อัตโนมัติ (เพื่อป้องกันการวนลูปเตะตัวเองออก)
                    await channel.connect(reconnect=False, self_deaf=True, timeout=20.0)
                    print(f'[SUCCESS] เข้าห้องสำเร็จ นิ่งยาวๆ แล้วครับ!', flush=True)
                    await asyncio.sleep(15)
                else:
                    print(f'[ERROR] ไม่พบ ID ห้องเสียงในระบบ', flush=True)

            except Exception as e:
                print(f'[VOICE-RETRY] รอการเชื่อมต่อใหม่รอบถัดไป... (Error: {e})', flush=True)
            
            # เว้นระยะห่างในการพยายามเชื่อมต่อใหม่ทุก 10 วินาที
            await asyncio.sleep(10)

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

client = AdminVoiceBot(intents=intents)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        client.run(TOKEN)
    else:
        print('[ERROR] ไม่พบ DISCORD_TOKEN ใน Environment Variables!', flush=True)
