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
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# ระบุ ID ของเซิร์ฟเวอร์ (Guild ID)
GUILD_ID = 1512058685168554054 

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="สิงห้องเสียง 24 ชม. 🟢"))
    client.loop.create_task(auto_join_voice())

async def auto_join_voice():
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    
    while not client.is_closed():
        try:
            if guild:
                # ค้นหาห้องเสียงที่มีคนนั่งอยู่ (เช่น ห้องที่คุณกำลังอยู่)
                target_channel = None
                for vc in guild.voice_channels:
                    # ถ้าเจอห้องที่มีคนอยู่ ให้เลือกห้องนั้นเลย
                    members_without_bots = [m for m in vc.members if not m.bot]
                    if len(members_without_bots) > 0:
                        target_channel = vc
                        break
                
                # หากไม่มีคนอยู่เลย ให้เลือกห้องเสียงแรกของเซิร์ฟเวอร์
                if not target_channel and len(guild.voice_channels) > 0:
                    target_channel = guild.voice_channels[0]

                if target_channel:
                    # เช็กว่าบอทยังไม่ได้เชื่อมต่อ หรือหลุดสายอยู่
                    if not client.voice_clients or not client.voice_clients[0].is_connected():
                        print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {target_channel.name}')
                        await target_channel.connect(reconnect=True, self_deaf=True)
                        print(f'[VOICE] เชื่อมต่อสำเร็จ!')
                    # ถ้าบอทอยู่คนละห้องกับคุณ ให้ย้ายตามมา
                    elif client.voice_clients[0].channel != target_channel and len(target_channel.members) > 1:
                        print(f'[VOICE] ย้ายตามเข้าห้อง: {target_channel.name}')
                        await client.voice_clients[0].move_to(target_channel)
        except Exception as e:
            print(f'[ERROR] Voice error: {e}')
        
        await asyncio.sleep(5)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    TOKEN = os.environ.get('DISCORD_TOKEN')
    client.run(TOKEN)
