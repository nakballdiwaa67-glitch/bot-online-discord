import os
import asyncio
import discord

# เปิดใช้งาน Intents ทั้งหมดเพื่อป้องกันปัญหาเรื่องสิทธิ์
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# ใส่ ID ห้องเสียงของคุณ
VOICE_CHANNEL_ID = 1512748513492992132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="สิงห้องเสียง 24 ชม. 🟢"))
    client.loop.create_task(keep_in_voice())

async def keep_in_voice():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            channel = client.get_channel(VOICE_CHANNEL_ID)
            if channel:
                if not client.voice_clients or not client.voice_clients[0].is_connected():
                    print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง: {channel.name}')
                    await channel.connect(reconnect=True, self_deaf=True)
                    print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            else:
                print(f'[ERROR] หาห้องเสียง ID: {VOICE_CHANNEL_ID} ไม่เจอ')
        except Exception as e:
            print(f'[ERROR] เกิดข้อผิดพลาด: {e}')
        
        await asyncio.sleep(10)

TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)
