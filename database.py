import mysql.connector as mysql
import datetime
from datetime import timedelta

# load api key
secret = {}
with open('secret.txt') as f:
    lines = f.readlines()
    for line in lines:
        secret[line.split("=")[0]] = line.split("=")[1].replace("\n", "")


def select_unite_setup_channel_ids():
    db = mysql.connect(host=secret['DBHOST'], user=secret['DBUSER'], passwd=secret['DBPASS'], database=secret['DBTABLE'])
    cursor = db.cursor()
    query = 'SELECT distinct(unite_setup_channel_id) FROM discord_guilds;'
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    db.close()
    #
    unite_setup_channels = []
    for record in records:
        unite_setup_channels.append(int(record[0]))
    return unite_setup_channels


def insert_guild(guild_id, guild_name, unite_setup_channel_id):
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = "INSERT INTO discord_guilds (guild_id, guild_name, unite_setup_channel_id, created_at) VALUES (%s, %s, %s, %s);"
    values = (guild_id, guild_name, unite_setup_channel_id, str(datetime.datetime.now()).split('.')[0])
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "guild inserted")
    cursor.close()
    db.close()


def insert_rule(guild_id, token_address, token_min, token_max, role_id, role_name):
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = "INSERT INTO discord_rules (guild_id, token_address, token_min, token_max, role_id, role_name, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    values = (guild_id, token_address, token_min, token_max, role_id, role_name, str(datetime.datetime.now()).split('.')[0])
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "record inserted")
    cursor.close()
    db.close()


def select_rules(guild_id):
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = f'SELECT token_address, token_min, token_max, role_id, role_name FROM discord_rules where guild_id = {guild_id};'
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    db.close()
    #
    rules = []
    for record in records:
        rule = dict(zip(['token_address', 'token_min', 'token_max', 'role_id', 'role_name'], record))
        rules.append(rule)
    return rules


def reset_rules(guild_id):
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = "DELETE from discord_rules where guild_id = %s;"
    values = (str(guild_id),)
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "record deleted")
    cursor.close()
    db.close()


def select_users():
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = f'SELECT account_id, user_ethereum_address FROM social_accounts;'
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    db.close()
    #
    users = []
    for record in records:
        users.append(dict(zip(['discord_user_id', 'ethereum_address'], record)))
    return users


def update_user(account_id):
    # update blockchain_write_time
    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = "UPDATE social_accounts SET blockchain_check_time=%s WHERE account_id=%s;"
    values = (str(datetime.datetime.now()).split('.')[0], account_id)
    cursor.execute(query, values)
    db.commit()
    print(f"Updated {values[1]} to {values[0]}")
    cursor.close()
    db.close()  

def select_users_to_check(hours_ago=4):
    datetime_check = datetime.datetime.now() - timedelta(hours=hours_ago)

    db = mysql.connect(host=secret['DBHOST'],user=secret['DBUSER'],passwd=secret['DBPASS'],database=secret['DBTABLE'])
    cursor = db.cursor()
    query = f'SELECT account_id, user_ethereum_address FROM unite_staging.social_accounts WHERE (blockchain_check_time <= "{str(datetime_check)}" OR blockchain_check_time IS NULL);;'
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    db.close()

    users = []
    for record in records:
        users.append(dict(zip(['account_id', 'ethereum_address'], record)))

    return users
