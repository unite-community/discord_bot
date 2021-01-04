#!/usr/bin/env python
# coding: utf-8

import discord
from discord.utils import find, get
from database import select_unite_setup_channel_ids, insert_guild, insert_rule, select_rules, reset_rules

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
    print(type(channel.id))
    insert_guild(guild.id, guild.name, channel.id)
    unite_setup_channels.append(channel.id)
    # send instructions to private channel
    msg = """
    **Welcome to the Unite setup process 🤝**

This channel is only visible to the admins of this Discord server and is used to configure the rules for channel access based on how many tokens users have.

You can use the following commands:

**'rules'** - display all existing rules

**'reset'** - delete all rules

**'addrule @role tokenaddress min max'** - for example, '`addrule @pro 0x87b008e57f640d94ee44fd893f0323af933f9195 10 100`' will add a rule that says only users with between 10 and 100 tokens (of the token with address 0x87b008e57f640d94ee44fd893f0323af933f9195) will be given the @pro role. You can use -1 for unlimited max.

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
                await message.channel.send("BRB processing...")
                rules = select_rules(message.guild.id)
                if len(rules) == 0:
                    await message.channel.send("No rules setup yet - try add one using `addrule`")
                    return
                else:
                    await message.channel.send(f"These {len(rules)} rules are running:")
                    for rule in rules:
                        await message.channel.send(str(rule))
                    return 

            if message.content.lower().replace("'", "").startswith('addrule'):
                await message.channel.send("BRB processing...")

                # add the rule to SQL database
                try:
                    # parse add rule command 
                    splits = message.content.lower().split(" ")
                    role_id = int(splits[1].replace("<", "").replace(">", "").replace("&", "").replace("@", ""))
                    token_address = splits[2]
                    token_min = int(splits[3])
                    token_max = int(splits[4])

                    # get role for name
                    role = get(message.guild.roles, id=role_id)

                    # write role to sql
                    insert_rule(message.guild.id, token_address, token_min, token_max, role_id, role.name)

                    await message.channel.send("Rule successfully added 🙌")

                except Exception as e:
                    await message.channel.send("Error adding rule 😭 ...please check command format")
                    print("ERROR", e)
                return

            if message.content.lower().replace("'", "").startswith('reset'):
                await message.channel.send("BRB processing...")
                rules = select_rules(message.guild.id)
                reset_rules(message.guild.id)
                if len(rules) > 0:
                    await message.channel.send(f"Deleted {len(rules)} rules")
                await message.channel.send("Done resetting rules - use `addrule` to set up a new rule")
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
