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
    
    # รัน Task เฝ้าห้องเสียง
    client.loop.create_task(keep_voice_alive())

async def keep_voice_alive():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                # ถ้ายังไม่มี Voice Client หรือไม่ได้เชื่อมต่ออยู่ ให้กดเข้าห้อง
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            else:
                print(f'[ERROR] หาห้องเสียง ID: {VOICE_CHANNEL_ID} ไม่เจอ')
        except Exception as e:
            print(f'[ERROR] Voice connection error: {e}')
        
        # เช็กสถานะทุกๆ 5 วินาที ถ้าโดนเตะหลุดจะเด้งกลับเข้ามาใหม่ทันที
        await asyncio.sleep(5)

TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)
