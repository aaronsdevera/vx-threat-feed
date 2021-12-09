################################################################
# import libraries
################################################################
import os
import csv
import json
import uuid
import time
import datetime
import discord

# es imports
from elasticsearch import Elasticsearch, helpers

################################################################
# import secrets
################################################################

# setup secrets dict
secrets = {}

# read the csv named secrets.csv
reader = csv.DictReader(open('../../.discord.csv'))
for row in reader:
    
    if row['service'] in secrets.keys():
        secrets[row['service']].update(
            {
                row['key']:row['value']
            }
        )
    else:
        secrets.update(
            {
                row['service']: {
                    row['key']:row['value']
                }
            }
        )




################################################################
# elastic search configuration
################################################################

# collector id and index name
CID = 'collector-discord-6c565d92'
INDEX = CID
ERRORINDEX = 'logs'

# set the elasticsearch endpoint
ES_ENDPOINT = ''
# set the elasticsearch post
ES_ENDPOINT_PORT = 9243
# extract elasticsearch api key from secrets
API_KEY = secrets['elastic']['api_key']
# extract elasticsearch password from secrets
ELASTIC_PASSWORD = secrets['elastic']['password']

# instantiate elastichsearch client
es = Elasticsearch(
            [ES_ENDPOINT],
            http_auth=('elastic', ELASTIC_PASSWORD),
            port=ES_ENDPOINT_PORT,
            api_key=API_KEY
        )




################################################################
# discord configuration
################################################################

# instantiate discord client
client = discord.Client()

# extract discord token from secrets
DISCORD_TOKEN = secrets['discord']['token']




################################################################
# functions
################################################################

# function to sent a dict to elasticsearch index
def sendToIndex(index: str, data: dict):
    return es.index(index=index, body=data)

# genDirectMessageURL
def genDirectMessageURL(recipient_id: str, message_id: str):
    return 'https://discord.com/channels/@me/{recipient_id}/{message_id}'.format(recipient_id=recipient_id,message_id=message_id)

# genMessageURL
def genMessageURL(channel_id: str,recipient_id: str, message_id: str):
    return 'https://discord.com/channels/{channel_id}/{recipient_id}/{message_id}'.format(channel_id=channel_id,recipient_id=recipient_id,message_id=message_id)

# function to extract the data from the raw message class to a dict
def classToJson(message,isDM: int):
    try:
        if isDM == 1:
            return {
                'message_id' : message.id,
                'recipient': message.channel.recipient.name,
                'recipient_id': message.channel.recipient.id,
                'recipient_bot': message.channel.recipient.bot,
                'author': message.author.name,
                'author_id': message.author.id,
                'author_bot': message.author.bot,
                'text': message.content
            }
        if isDM == 0:
            return {
                'message_id' : message.id,
                'channel' : message.channel.name,
                'channel_id': message.channel.id,
                'channel_category_id': message.channel.category_id,
                'author': message.author.name,
                'author_id': message.author.id,
                'author_bot': message.author.bot,
                'guild': message.guild.name,
                'guild_id' : message.guild.id,
                'guild_size': message.guild.member_count,
                'text': message.content
            }
    except:
        
        return {
            'status' : 'error',
            'message' : str(e)
        }



################################################################
# event handling
################################################################

# hangle message on client event
@client.event
async def on_message(message):

    # stupid way to detect DM vs Public chanels
    isDM = 0
    if 'channel=<DMChannel ' in str(message):
        isDM = 1

    # create a unique identifier for the event
    uid = str(uuid.uuid4()).replace('-','')
    
    # generate a timestamp
    ts = datetime.datetime.utcnow()
    
    # instantiate data dict
    data = {}
    msg = {}
    source = ''
    thread = ''

    # attempt to extract
    try:
        # do the class extraction
        msg = classToJson(message,isDM)

        # just dont even run if there is no post body
        if msg['text'] == '':
            exit
        
        # did classToJson() produce an error? check 1
        if 'status' in msg.keys():
            # did classToJson() produce an error? check 2
            if msg['status'] == 'error':

                # assemble error data
                data = {
                    '@timestamp' : ts,
                    'subproduct':'collections',
                    'cid':CID,
                    'status' : msg['status'],
                    'message' : msg['message']
                }
                # send error data
                sendToIndex(ERRORINDEX,data)
                exit
                
    except Exception as e:
        # assemble error data
        data = {
            '@timestamp' : ts,
            'subproduct':'collections',
            'cid':CID,
            'status' : msg['status'],
            'message' : msg['message']
        }
        # send error data
        sendToIndex(ERRORINDEX,data)
        exit
    
    try:
        # determine the URL
        url = ''
        # is the message a DM? check 1
        if isDM == 1:
            # generate message URL knowing it's a DM
            url = genDirectMessageURL(
                recipient_id=msg['author_id'],
                message_id=msg['message_id']
            )
            # gonna map the discord server to source
            source = 'Direct message with {author}'.format(author=msg['author'])
            # thread is mapped to the channel in the server
            thread = 'Direct message with {author}'.format(author=msg['author'])
        
        # confirm that the message is not a DM
        if isDM == 0:
            # generate the message URL knowing its not a DM
            url = genMessageURL(
                channel_id=msg['channel_id'],
                recipient_id=msg['author_id'],
                message_id=msg['message_id']
            )
            # gonna map the discord server to source
            source = msg['guild']
            # thread is mapped to the channel in the server
            thread = msg['channel']
            

        # author is the username of the message author
        author = msg['author']
        # post is the actual text contents in full
        post = msg['text']

        # assemble the output data
        data = {
            '@timestamp':ts,
            'source':source,
            'thread':thread,
            'author':author,
            'post':post,
            'url':url
        }
        # send to index
        sendToIndex(INDEX,data)

    except Exception as e:
        # assemble error data
        data = {
            '@timestamp' : ts,
            'subproduct':'collections',
            'cid':CID,
            'status' : 'error',
            'message' : str(e)
        }
        # send error data
        sendToIndex(ERRORINDEX,data)



################################################################
# let it rip
################################################################

# run it run it
client.run(DISCORD_TOKEN, bot=False)
