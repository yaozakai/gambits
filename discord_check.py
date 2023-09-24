import csv

import discord

from constants import DISCORD_BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    file = open('static/csv/discord_memberlist.csv', 'w', encoding='utf-8-sig')
    member_list = csv.writer(file)
    row = []
    row2 = []

    for guild in client.guilds:
        for member in guild.members:
            print(member)
            row.append(member)
            member_list.writerow(row)
            row.clear()
    file.close()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

client.run(DISCORD_BOT_TOKEN)
