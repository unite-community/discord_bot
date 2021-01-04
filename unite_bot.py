#!/usr/bin/env python
# coding: utf-8

import discord
from discord.utils import find
from database import select_unite_setup_channel_ids, insert_guild

# load api key
secret = {}
with open('secret.txt') as f:
    lines = f.readlines()
    for line in lines:
        secret[line.split("=")[0]] = line.split("=")[1].replace("\n","")

# init client
client = discord.Client()

# load list of unite setup channel ids
unite_setup_channels = select_unite_setup_channel_ids()
print(f"Loaded {len(unite_setup_channels)} unite setup channel ids")


########################
### SETUP DISCORD EVENTS
########################

@client.event
async def on_ready():
    print('Discord bot running as {0.user}'.format(client))


@client.event
async def on_guild_join(guild):

    # post hello message
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}!'.format(guild.name))

    # create private channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        # guild.owner: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel('unite-setup', overwrites=overwrites)

    # save guild with unite setup channel id 
    # this is so that we can listen for messages in that channel
    print(f"Created channel {channel.id} - {channel.name} in guild {guild.id} - {guild.name}")
    insert_guild(guild.id, guild.name, channel.id)
    unite_setup_channels.append(channel.id)
    # send instructions to private channel
    msg = """
    **Welcome to the Unite bot setup process**

This channel is only visible to the admins of this Discord server and is used to configure the rules for channel access based on how many tokens users have.

You can use the following commands:
**'rules'** - display all existing rules
**'addrule'** - add new rule for channel access based on user token holdings
**'reset'** - delete all rules
    """
    await channel.send(msg)


@client.event
async def on_message(message):
    # debug
    print(f"{message.author} ({message.channel.id} - {message.channel.name}) {message.content}")

    if message.author == client.user:
        return

    if message.content.startswith('!setup'):
        await message.channel.send("Hello " + message.author.name)

    #######################
    ### unite setup channel
    #######################
    try:
        if message.channel.id in unite_setup_channels:
            print("message is in setup channel")

            if message.content.lower().startswith('hello') or message.content.lower().startswith('hi'):
                await message.channel.send("hello")
                return

            if message.content.lower().replace("'", "").startswith('rules'):
                await message.channel.send("DO RULES")
                # TODO: list rules
                return 

            if message.content.lower().replace("'", "").startswith('addrule'):
                await message.channel.send("DO ADD RULE")
                # TODO: add rule
                return

            if message.content.lower().replace("'", "").startswith('reset'):
                await message.channel.send("DO RESET")
                # TODO: reset rules
                return

            # unrecognized input
            msg = """
Sorry but that command is not recognized...

Please try type one of 'rules', 'addrule', or 'reset'

You can also message us in the Unite Discord: https://discord.gg/EBJEgVB8us if you're stuck.
            """
            await message.channel.send(msg)
            return

    except Exception as e:
        print(e)

client.run(secret['TOKEN'])
