# Unite Discord bot

Discord bot for updating user roles in a Discord server based on token holdings. 

The user will invite the bot to their discord and the bot will create private channel for user to set up rules that map token holdings to Discord roles for the users in the discord server being configured. 

It automatically monitors user balances and updates roles when balances do not meet user-defined rules.

## Setup 
Go to the Discord [developer site](https://discordapp.com/developers/applications/me) to create an application with the following permissions:

* "Server Members Intent" permission under `Bot -> Priveleged Gateway Intents` section of the Discord Developer Portal for the bot.
* Send Messages
* Manage Roles
* Manage Channels



Save the discord bot credentials `client id` and `client secret` in `secret.txt` which also needs to include SQL connection details and Infura details.

```json
CLIENTID=1234...
SECRET=ABCD...
DBHOST=12.34.56.78
DBUSER=abc...
DBPASS=abc...
DBTABLE=abc...
```

Install dependencies
> `pip install -r requirements.txt`

Run
> `python unite_bot.py`


## Using the bot
1. Invite the bot to the discord channel using the invite link:
> https://discord.com/api/oauth2/authorize?client_id=789456739023192075&permissions=268437520&scope=bot

2. Bot will create `unite-setup` channel - follow instructions to set up rules e.g. 
> addrule @level 1 0x87b008e57f640d94ee44fd893f0323af933f9195 1 10


## Todo
* remove roles if balance not satisfied
* run rules assignment process on schedule
* //
* pull role names in rules list from guild instead of db (in case they were edited)
* make roles use proper embeds so they display coloured and highlighted
* message user telling them roles updated
* send image showing how to re-order roles
* don't re-assign role if already satisfied
* get balance once for all rules (assuming we decide only 1 token sets the rules)
* DM alex / sebastian on errors / rate limits