import os
import time
from slackclient import SlackClient


BOT_NAME = 'xibot'
BOT_ID = 'U7MC33TL1'
WEBSOCKET_DELAY = 1
slack_client = SlackClient("xxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx")


if slack_client.rtm_connect():
    print("StarterBot connected and running!")
    while True:
        response = ":)"
        slack_client.api_call("chat.postMessage", channel='xinit',
                          text=response, as_user=True)
        time.sleep(WEBSOCKET_DELAY)
