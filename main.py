import os
import asyncio
import threading
from flask import Flask
import discord

# --- Web Server หลอก Render ไม่ให้สั่งดับ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Discord Bot Class ---
# 📌 ใส่ ID ห้องเสียง "ทำงานแอดมิน" ตรงนี้
VOICE_CHANNEL_ID = 1512748513492902132

class AdminVoiceBot(discord.Client):
    async def setup_hook(self):
        # รัน Task เฝ้าห้องเสียงทันทีที่เริ่มรันระบบ
        self.loop.create_task(self.keep_voice_alive())

    async def keep_voice_alive(self):
        await self.wait_until_ready()
        print(f'[ONLINE] บอท {self.user} ออนไลน์เรียบร้อยแล้ว!')
        await self.change_presence(activity=discord.Game(name="สิงห้องแอดมิน 24 ชม. 🟢"))
        
        while not self.is_closed():
            try:
                channel = self.get_channel(VOICE_CHANNEL_ID)
                if channel:
                    # ถ้ายังไม่ได้เชื่อมต่อ ให้กดเข้าห้อง
                    if not self.voice_clients or not self.voice_clients[0].is_connected():
                        print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}')
                        await channel.connect(reconnect=True, self_deaf=True)
                        print(f'[VOICE] ดึงบอทเข้าห้องสำเร็จ!')
                else:
                    print(f'[ERROR] หาห้อง ID: {VOICE_CHANNEL_ID} ไม่เจอ ตรวจสอบ ID หรือสิทธิ์บอทอีกครั้ง')
            except Exception as e:
                print(f'[ERROR] Voice loop error: {e}')
            
            # ตรวจเช็กสถานะทุกๆ 5 วินาที
            await asyncio.sleep(5)

intents = discord.Intents.default()
client = AdminVoiceBot(intents=intents)

if __name__ == '__main__':
    # รัน Web Server แยกใน Background Thread
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # รัน Discord Bot
    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
