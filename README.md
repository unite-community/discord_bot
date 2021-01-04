# Unite Discord Userlist bot

## Setup
Follow these steps to set up bot permissions:
https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

It also needs the following permissions:
* "Server Members Intent" permission under `Bot -> Priveleged Gateway Intents` section of the Discord Developer Portal for the bot.
* Send Messages
* Manage Roles
* Manage Channels


## Running the bot
Run `python unite_bot.py`


## Using the bot
1. Invite the bot to the discord channel using the invite link:
> https://discord.com/api/oauth2/authorize?client_id=789456739023192075&permissions=268437520&scope=bot

2. Bot will create `unite-setup` channel - follow instructions to set up rules



## Todo
* check for overlapping / invalid rules
* pull role names from guild instead of db (in case they were edited)




## Architecture v1

### Setting up discord to use token-gated access
1. click bot invite link and add bot to your discord
2. bot creates private channel and messages in it saying nobody can see it, tells you to set up roles then addrole etc.
3. displays all available roles and says type !addrule @role min max token
4. saves role params to `discord_roles` sql table (guild_id, role_id, token_address, min, max) and triggers running roles assignment process
5. run role assignment process

### Role assignment process
1. get all rules
2. get all users in discord_roles table
3. get all users across guilds that the bot is installed on. for each user:
3.1. if user in users: get token balance for their wallet
3.2. update roles based on rules

### Initializing discord roles
1. click link to unite page.
2. log in using wallet
3. click discord oauth link - pass wallet in link 
4. saves discord:wallet:guild mapping in `discord_members` sql table (wallet, guild_id, discord_username)
5. checks token balance for this wallet then loops over `discord_roles` rows and adds/removes user roles
6. bot updates roles and invites you to discord

### Scheduled roles assignemnt process
every 4 hours:
1. checks token balance for this wallet then loops over `discord_roles` rows and adds/removes user roles




