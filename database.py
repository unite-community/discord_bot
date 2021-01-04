import mysql.connector as mysql
import datetime

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
        unite_setup_channels.append(record[0])
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
