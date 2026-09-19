import os
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ใส่ ID ของห้องเสียงที่ต้องการให้บอทเข้าไปสิง (ตัวเลข)
VOICE_CHANNEL_ID = 1512748513492992132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="ออนไลน์ในห้องเสียง 24 ชม. 🟢"))
    
    # สั่งให้บอทเดินเข้าห้องเสียงอัตโนมัติเมื่อออนไลน์
    try:
        channel = client.get_channel(VOICE_CHANNEL_ID)
        if channel:
            await channel.connect()
            print(f'[VOICE] ดึงบอทเข้าห้อง {channel.name} สำเร็จ!')
        else:
            print('[ERROR] หาห้องเสียงไม่เจอ ตรวจสอบ ID อีกครั้ง')
    except Exception as e:
        print(f'[ERROR] ไม่สามารถเข้าห้องเสียงได้: {e}')

TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)
