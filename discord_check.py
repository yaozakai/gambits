import csv
from queue import Queue
from threading import Thread

import discord

from constants import DISCORD_BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

q = Queue()


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


    # await client.close()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')


def update_users():
    client.run(DISCORD_BOT_TOKEN)


# thread = Thread(target=update_users, args=(q))


async def check_discord(user):
    if check_discord_CSV(user):
        return True
    else:
        await update_users()
        return check_discord_CSV(user)


def check_discord_CSV(user):
    reader = csv.DictReader(open('static/csv/discord_memberlist.csv', mode='r', encoding='utf-8-sig'))
    for row in reader:
        if user.name is row['name']:
            return True
    return False

