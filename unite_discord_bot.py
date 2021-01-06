#!/usr/bin/env python
# coding: utf-8

import json
import discord
from discord.utils import find, get
from web3 import Web3
from database import select_unite_setup_channel_ids, insert_guild, insert_rule, select_rules, reset_rules, select_users


# load api key
secret = {}
with open('secret.txt') as f:
    lines = f.readlines()
    for line in lines:
        secret[line.split("=")[0]] = line.split("=")[1].replace("\n", "")

################
### INIT DISCORD
################

# init discord client
client = discord.Client()

# load list of unite setup channel ids
unite_setup_channels = select_unite_setup_channel_ids()
print(f"Loaded {len(unite_setup_channels)} unite setup channel ids")


#############
### INIT WEB3
#############

# load erc20 abi for fetching token balance
with open('abi_erc20.json') as f:
    abi = json.load(f)

# init web3
infura_url = secret['INFURAURL1']
web3 = Web3(Web3.HTTPProvider(infura_url))
print(f"Connected to infura: {infura_url}")

# define function to get erc20 token balance for a wallet
def get_wallet_erc20_balance(wallet, token):
    contract = web3.eth.contract(abi=abi, address=Web3.toChecksumAddress(str(token)))
    raw_balance = contract.functions.balanceOf(wallet).call()
    balance = raw_balance/10**(contract.functions.decimals().call())
    print(f"wallet {wallet} has {balance} tokens")
    return balance

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
        await general.send('Hello World')

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


    # send instructions in new private unite setup channel
    msg = """

This channel is only visible to the admins of this Discord server and is used to configure the rules for channel access based on how many tokens users have.

Channel access is managed by assigning users roles and limiting channels to specific roles. Before you configure rules for which roles are assigned based on token balances, you should first set up the roles you want to assign to users. 

Once you have set up roles, you need to set up rules that determine how many tokens a user needs to be assigned a role:

You can use the following commands:
**'rules'** - display all existing rules
**'reset'** - delete all rules
**'addrule @role tokenaddress min max'** - for example, '`addrule @pro 0x87b008e57f640d94ee44fd893f0323af933f9195 10 100`' will add a rule that says only users with between 10 and 100 tokens (of the token with address 0x87b008e57f640d94ee44fd893f0323af933f9195) will be given the @pro role. You can use -1 for unlimited max.

You can also message us in the Unite Discord if you need help:
    """
    embed = discord.Embed()
    embed.add_field(name="Welcome to the Unite setup process 🤝", value=msg)
    await channel.send(embed=embed)
    await channel.send("https://discord.gg/EBJEgVB8us")

    # reset rules - mostly for debugging
    reset_rules(guild.id)


@client.event
async def on_message(message):
    # debug
    # print(f"{message.author} ({message.channel.id} - {message.channel.name}) {message.content}")

    if message.author == client.user:
        return


    #######################
    ### unite setup channel
    #######################
    try:
        if message.channel.id in unite_setup_channels:


            if message.content.startswith('test'):
                async for member in message.guild.fetch_members(limit=None):
                    print("{},{},{},{}".format(message.guild, member, member.id, member.display_name))
                return


            if message.content.lower().startswith('hello') or message.content.lower().startswith('hi'):
                await message.channel.send("Hi " + message.author.name.split(" ")[0])
                return

            if message.content.lower().replace("'", "").startswith('rules'):
                await message.channel.send("processing BRB...")

                # get rules and loop over them to build reply
                rules = select_rules(message.guild.id)
                if len(rules) == 0:
                    await message.channel.send("No rules setup yet - try add one using `addrule`")
                    return
                else:
                    if len(rules) == 1:
                        msg_title = "This 1 rule is running:"
                    else:
                        msg_title = f"These {len(rules)} rules are running:\n"

                    msg = ""
                    for i, rule in enumerate(rules):
                        msg +=f"""
{i+1}.
**token_address**: {rule['token_address']}
**role**: {rule['role_name']}
**minimum tokens required**: {rule['token_min']}
**maximum tokens required**: {rule['token_max']}
"""

                    # send rules msg
                    embed = discord.Embed()
                    embed.add_field(name=msg_title, value=msg)
                    await message.channel.send(embed=embed)

                    return 

            if message.content.lower().replace("'", "").startswith('addrule'):
                await message.channel.send("processing BRB...")

                # add the rule to SQL database
                try:
                    # parse add rule command 
                    splits = [s.strip() for s in message.content.lower().split(" ")]
                    role_id = int(splits[1].replace("<", "").replace(">", "").replace("&", "").replace("@", ""))
                    token_address = splits[2]
                    token_min = int(splits[3])
                    token_max = int(splits[4])
                    if token_max == -1:
                        token_max = None

                    # get role for name
                    role = get(message.guild.roles, id=role_id)

                    # write role to sql
                    insert_rule(message.guild.id, token_address, token_min, token_max, role_id, role.name)

                    await message.channel.send("Rule successfully added 🙌")

                    #####################
                    ### RUN RULES PROCESS
                    #####################

                    await message.channel.send("Running roles update process...")

                    # select users
                    users = select_users()

                    # create list and dict for lookups
                    user_ids = [int(u['discord_user_id']) for u in users]
                    user_wallets = {int(u['discord_user_id']): u['ethereum_address'] for u in users}

                    roles_updated = 0
                    async for member in message.guild.fetch_members(limit=None):
                        print("{},{},{},{}".format(message.guild, member, member.id, member.display_name))
                        if member.id in user_ids:
                            print(f"User match {member.id} - begin roles process")

                            # get wallet for this user
                            wallet = user_wallets[member.id]

                            # get user balance for this token
                            balance = get_wallet_erc20_balance(wallet, token_address)
                            print(f"Token {token_address} balance for user: {balance}")

                            # get rule ranges
                            if token_max is None:
                                token_max = 999999999999999999

                            if balance >= token_min and balance <= token_max:
                                print("rule satisfied - assigning role")
                                roles_updated += 1
                                # assign role
                                role = get(message.guild.roles, id=int(role_id))
                                await member.add_roles(role)
                                print(f"assigned {role} to {member}")
                            else:
                                print("rule not satisfied")
                    await message.channel.send(f"{roles_updated} roles updated")
                    return

                except Exception as e:
                    await message.channel.send("Error adding rule 😭 ...please check command format")
                    print("ERROR", e)
                return

            if message.content.lower().replace("'", "").startswith('reset'):
                await message.channel.send("processing BRB...")
                rules = select_rules(message.guild.id)
                reset_rules(message.guild.id)
                if len(rules) > 0:
                    await message.channel.send(f"Deleted {len(rules)} rules")
                await message.channel.send("Done resetting rules - use `addrule` to set up a new rule")
                # TODO: reset rules
                return

            # unrecognized input
            msg = """

You can use the following commands:

**'rules'** - display all existing rules

**'reset'** - delete all rules

**'addrule @role tokenaddress min max'** - for example, '`addrule @pro 0x87b008e57f640d94ee44fd893f0323af933f9195 10 100`' will add a rule that says only users with between 10 and 100 tokens (of the token with address 0x87b008e57f640d94ee44fd893f0323af933f9195) will be given the @pro role. You can use -1 for unlimited max.

You can also message us in the Unite Discord if you need help:
https://discord.gg/EBJEgVB8us
            """
            embed = discord.Embed()
            embed.add_field(name="Sorry but that command is not recognized...", value=msg)
            await message.channel.send(embed=embed)
            return

    except Exception as e:
        print(e)

client.run(secret['TOKEN'])
