import os
import json
import logging
import requests
 
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

TOKEN = 'xoxb-xxxx'
SLACK_CHANNEL = '#mail-feed'
 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
 
def lambda_handler(event, context):
 
    print(json.dumps(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])

    tmpJson = requests.post(
        f'https://slack.com/api/chat.postMessage',
        data={'token':TOKEN,
        'channel':message["channel"],
        'text':message["message"]}
    ).json()
    
    print(tmpJson)
