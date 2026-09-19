import os
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ใส่ ID ห้องเสียงของคุณที่นี่ (ตัวเลข)
VOICE_CHANNEL_ID = 1512748513492902132

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="ออนไลน์ในห้องเสียง 24 ชม. 🟢"))
    
    try:
        channel = client.get_channel(VOICE_CHANNEL_ID)
        if channel:
            # ใช้ self_deaf=True เพื่อให้บอทหูหนวกอัตโนมัติ ช่วยลดภาระเน็ตและเข้าห้องได้ไวยิ่งขึ้น
            await channel.connect(reconnect=True, self_deaf=True)
            print(f'[VOICE] ดึงบอทเข้าห้องสำเร็จ!')
        else:
            print('[ERROR] หาห้องเสียงไม่เจอ ตรวจสอบ ID อีกครั้ง')
    except Exception as e:
        print(f'[ERROR] เกิดข้อผิดพลาด: {e}')

TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)
