import os
import asyncio
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ใส่ ID ห้องเสียงของคุณ
VOICE_CHANNEL_ID = 1512748513492902132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="สิงห้องเสียง 24 ชม. 🟢"))
    
    # รันลูปเฝ้าห้องเสียงในพื้นหลัง
    client.loop.create_task(keep_in_voice())

async def keep_in_voice():
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                # ถ้ายังไม่ได้เข้าห้องเสียง หรือสายหลุด ให้เชื่อมต่อใหม่
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง {channel.name}...')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            else:
                print('[ERROR] หา ID ห้องเสียงไม่เจอ')
        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาดในห้องเสียง: {e}')
        
        # เช็กสถานะทุกๆ 10 วินาที
        await asyncio.sleep(10)

TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)
