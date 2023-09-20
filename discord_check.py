import discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(f'Checking member is here')
    for guild in client.guilds:
        for member in guild.members:
            print(member)
            if member == 'saved_member_name':
                break


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


def run():
    client.run('MTE1Mzk5NjEyNDgxOTAzNDExMg.G5GUEg.ukdQUQULVvIM7ZJnb_g0IQYVEU4BssU6S94FXE')
