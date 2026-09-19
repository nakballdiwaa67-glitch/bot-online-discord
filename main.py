import os
import asyncio
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ใส่ ID ห้องเสียงของคุณ
VOICE_CHANNEL_ID = 1512748513492902132

async def join_and_stay_voice():
    await client.wait_until_ready()
    channel = client.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        print('[ERROR] หาห้องเสียงไม่เจอ')
        return

    while not client.is_closed():
        try:
            # เช็กว่าบอทเชื่อมต่อห้องเสียงอยู่หรือไม่
            if not client.voice_clients:
                print(f'[VOICE] กำลังเชื่อมต่อเข้าห้อง {channel.name}...')
                await channel.connect(reconnect=True, self_deaf=True)
                print(f'[VOICE] เชื่อมต่อสำเร็จ!')
            elif not client.voice_clients[0].is_connected():
                print('[VOICE] การเชื่อมต่อหลุด กำลังต่อใหม่...')
                await client.voice_clients[0].disconnect(force=True)
                await channel.connect(reconnect=True, self_deaf=True)
        except Exception as e:
            print(f'[ERROR] Voice loop error: {e}')
        
        # เช็กสถานะทุกๆ 15 วินาที
        await asyncio.sleep(15)

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="สิงห้องเสียง 24 ชม. 🟢"))

async def main():
    async with client:
        # รันงานเฝ้าห้องเสียงควบคู่ไปกับการทำงานของบอท
        client.loop.create_task(join_and_stay_voice())
        TOKEN = os.environ.get('DISCORD_TOKEN')
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
