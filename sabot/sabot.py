import os
import re
import logging
from typing import Callable

from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from helpers.elastic_helper import esConnect, esInsert
from helpers.general import unix2ts
from helpers.discourse import createTopic


logging.basicConfig(level=logging.DEBUG)

app = App()


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
        logger.debug(body)
        return next()

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# setup elastic cloud connection
es_cloud_id = os.getenv('sabot_cloud_id')
es_cloud_user = os.getenv('sabot_cloud_es_user')
es_cloud_pass = os.getenv('sabot_cloud_es_pass')
logging.info('Calling esConnect')
es = esConnect(es_cloud_id, es_cloud_user, es_cloud_pass)


# Discourse connection info
dAPI = 'dd7cbb74f9acfa2577518330ef98b471d2c3e1489b6ef6f808cb895fb0d35289'
dUser= 'jeff'
dServer = 'https://sa-hivemind.jeffvestal.com'


def get_user_info(userid):
    userInfo = app.client.users_info(
        user=userid
        )
    return userInfo



@app.command("/hello-socket-mode")
def hello_command(ack, body,logger: logging.Logger):
    logger.debug('hello')
    user_id = body["user_id"]
    ack(f"Hi, <@{user_id}>!")


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


@app.event("app_mention")
def event_test(say,logger: logging.Logger):
    print('app_mention')
    say("Hi there!")


@app.event("reaction_added")
def store_useful_info(event, say, context: BoltContext, client: WebClient, logger: logging.Logger):
    logger.debug(event)

    #say('I see a reaction')
    #logger.debug('type: %s' % event['type'])
    #logger.debug('user: %s' % event['user'])
    #logger.debug('reaction: %s' % event['reaction'])
    #logger.debug('type.channel: %s' % event['item']['channel'])
    #logger.debug('type.ts: %s' % event['item']['ts'])
    #logger.debug('context: %s' % context)


    # Send back reaction to ack
    client.reactions_add(
        #name="wave",
        name="white_check_mark",
        channel=event['item']['channel'],
        timestamp=event['item']['ts']
    )

    ## Find original message
    # ID of channel that the message exists in
    conversation_id = event['item']['channel']

    try:
        # Call the conversations.history method using the WebClient
        # The client passes the token you included in initialization
        result = client.conversations_history(
            channel=conversation_id,
            inclusive=True,
            oldest=event['item']['ts'],
            limit=1
        )

        message = result["messages"][0]
        logger.debug(message)


        # Build payload to sent to elastic
        payload = {
            'reaction' : {
                'user' : event['user'],
                'reaction' : event['reaction'],
                'channel' : event['item']['channel'],
                'reaction_ts' : event['event_ts']
                },
                'message_ts' : event['item']['ts'],
                'channel' : event['item']['channel'],
            'author': message['user'],
            'message' : message['text']
            }

        pl_resp = app.client.chat_getPermalink(
                channel = conversation_id,
                message_ts = event['item']['ts']
                )


        # Get user's real name
        logging.info('calling get_user_info')
        ui = get_user_info(event['user'])
        logging.debug(ui)
        payload['name'] = ui['user']['name']
        payload['real_name'] = ui['user']['real_name']

        # Get permalink
        if 'permalink' in pl_resp:
            logging.debug('Adding permalink info')
            payload['slack_link'] = pl_resp['permalink']
        elif 'error' in pl_resp:
            logging.error('Unable to get message permalink - %s' % pl_resp['error'])


        # Convert unix timestamps to datetime for es
        try:
            payload['message_timestamp'] = unix2ts(event['item']['ts'])
            payload['reaction_ts'] = unix2ts(event['event_ts'])

        except Exception as e:
            logging.error('error converting ts timestamp - %s' % e)



        # If there were any attachments grab the info about them and add to the payload
        if 'files' in message:
            logging.debug('Adding permalink info')
            payload['files'] = []

            for f in message['files']:
                payload['files'].append({
             	'filetype' : f['filetype'],
             	'permalink' : f['permalink'],
        #     	'thumb_800' : f['thumb_800'],
             	'title' : f['title'],
             	'user': f['user']
                    }
                )


        logging.debug('payload built - %s' % payload)
        resp = esInsert(es, payload)

        # post to discourse
        logging.debug('payload - %s' % payload)
        dpayload ={
                'title': payload['message'][:51],
                'raw':payload['message'] + 'From: %s - %s' % (payload['real_name'], payload['slack_link'])
                }
        logging.debug('DISCOURSE PAYLOAD - %s' % dpayload)
        createTopic(dpayload, dAPI, dUser, dServer)

    except SlackApiError as e:
        print(f"Error: {e}")
	#TODO send back sad failed reaction or something

    #TODO reply with some emojie and maybe ask to tag the message


#def sendToElastic(es, slack



## download file/screenshot attachments
# message[files] =[ {'url_private_download': 'https://files.slack.com/files-pri/T03P97LMYGY-F03NB53GKJB/download/blue_duck.png', {}...] }






if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s', level=logging.INFO)
    logging.info('Starting up')

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


