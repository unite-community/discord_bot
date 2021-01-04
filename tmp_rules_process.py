
# select rules
rules = select_rules(message.guild.id)

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

        for rule in rules:
            # get user balance for this token
            balance = get_wallet_erc20_balance(wallet, rule['token_address'])
            print(f"Token {rule['token_address']} balance for user: {balance}")

            # get rule ranges
            token_min = rule['token_min']
            token_max = rule['token_max']
            if token_max is None:
                token_max = 999999999999999999

            if balance >= token_min and balance <= token_max:
                print("rule satisfied - assigning role")
                roles_updated+=1
                # assign role
                role = get(message.guild.roles, id=int(rule['role_id']))
                await member.add_roles(role)
                print(f"assigned {role} to {member}")
            else:
                print("rule not satisfied")
await message.channel.send(f"{roles_updated} roles updated")
return