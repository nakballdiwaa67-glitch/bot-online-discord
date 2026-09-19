import os
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'[ONLINE] บอท {client.user} ออนไลน์เรียบร้อยแล้ว!')
    await client.change_presence(activity=discord.Game(name="ออนไลน์ 24 ชม. 🟢"))

# ดึง Token จากระบบ Cloud แทนการเขียนค้างไว้ในไฟล์
TOKEN = os.environ.get('DISCORD_TOKEN')
client.run(TOKEN)