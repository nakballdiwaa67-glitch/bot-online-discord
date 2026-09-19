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

# --- Discord Bot ---
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# 📌 เอา ID ของห้อง "พูดคุยรุ่นใหญ่" มาใส่ตรงนี้ครับ (วางแทนตัวเลขเดิมได้เลย)
VOICE_CHANNEL_ID = 1512748513492902132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="ชิว 24 ชม. 🟢"))
    client.loop.create_task(keep_voice_alive())

async def keep_voice_alive():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                # ถ้าหลุด หรือยังไม่ได้เข้าห้อง ให้กดเข้าห้องทันที
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}')
                    # self_deaf=True เพื่อให้ปิดหูและปิดไมค์อัตโนมัติแบบในรูป
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            else:
                print(f'[ERROR] หาห้อง ID: {VOICE_CHANNEL_ID} ไม่เจอ')
        except Exception as e:
            print(f'[ERROR] Voice error: {e}')
        
        # เช็กความเคลื่อนไหวทุกๆ 5 วินาที
        await asyncio.sleep(5)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
