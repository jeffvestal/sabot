import os
import re
import logging
from pprint import pprint
from typing import Callable

import elasticapm



from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from helpers.elastic_helper import esConnect, esInsert, esUpdateTag, listTags, searchMessages, searchMessagesAdvanced, buildAdvancedSearchBlock, esAppSearchConnect, searchDocs, searchBlogs
from helpers.general import unix2ts
from helpers.discourse import createTopic
from helpers.slack_helpers import buildTagsForm, buildSecondaryTags, parseCommands, helpCommands, combineBlocks, parseAdvSearchOptions


logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s'
                   )

# apm
logging.info('Creating Elastic APM client')
apmService = os.getenv("ELASTIC_APM_SERVICE_NAME")
apmHost = os.getenv("ELASTIC_APM_SERVER_URL")
apmSecret = os.getenv("ELASTIC_APM_SECRET_TOKEN")

apmClient = elasticapm.Client(service_name=apmService, server_url=apmHost, secret_token=apmSecret, environment='production')
logging.info('APM client created')
elasticapm.instrument()
#apm_logger = logging.getLogger("elasticapm")
#apm_logger.setLevel(logging.DEBUG)



app = App()

@elasticapm.capture_span()
@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
        logger.info('Starting log_request')
        logger.debug(body)

        apmClient.begin_transaction(transaction_type="log_request")
        return next()
        apmClient.end_transaction(name=__name__, result="success")

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# setup elastic cloud connection
es_cloud_id = os.getenv('sabot_cloud_id')
es_cloud_user = os.getenv('sabot_cloud_es_user')
es_cloud_pass = os.getenv('sabot_cloud_es_pass')
logging.info('Calling esConnect')
es = esConnect(es_cloud_id, es_cloud_user, es_cloud_pass)

# setup elastic App Search connection
as_url = os.getenv('sabot_appsearch_url')
as_api = os.getenv('sabot_appsearch_api')
logging.info('creating App Search Connection')
appsearch = esAppSearchConnect(as_url, as_api)


# Discourse connection info
discourse_api = os.getenv('discourse_api')
discourse_user = os.getenv('discourse_user')
discourse_server = os.getenv('discourse_server')


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


@elasticapm.capture_span()
@app.event("message")
def handle_message_events(body, logger):
    logger.debug('Processing event - message')
    logger.info(body)

@elasticapm.capture_span()
@app.event("app_mention")
def app_mention(say, client, ack, respond, payload, logger: logging.Logger):

    apmClient.begin_transaction(transaction_type="app_mention")
    logger.info('processing app_mention')
    ack()
    logger.debug(payload)

    # Send back reaction to ack
    client.reactions_add(
        name="sabot",
        channel=payload['channel'],
        timestamp=payload['ts']
    )

    # process the command
    logging.debug('sending payload to parse for command %s' % payload)
    command, rest = parseCommands(payload)

    logging.info('command %s' % command)
    logging.info('rest %s' % rest)

    if command == 'help':
        text = helpCommands()

    elif command == 'listtags':
        #maybe also for list ?
        text = listTags(es)

    elif command == 'search':
        if rest == [] or rest == ['advanced']:
             text = buildAdvancedSearchBlock()
        else:
            text = searchMessages(payload, es)

    elif command == 'docs':
        logging.info('Calling searchDocs')
        text = searchDocs(payload, rest, appsearch)

    elif command == 'blogs':
        logging.info('Calling searchBlogs')
        text = searchBlogs(payload, rest, appsearch)

    else:
        text = '''I don't recognize that command, below is the commands I know:\n\n%s''' % helpCommands()

    slack_user_id = payload["user"]
#    say(text)
#    say(text=text,
    say(text='test',
       blocks = text

       )

    apmClient.end_transaction(name=__name__, result="success")

    #client.chat_postEphemeral(
    #    channel=payload["channel"],
    #    user=slack_user_id,
    #    text=f"Howdy <@{slack_user_id}> Only you should be able to see this..."
    #)


@elasticapm.capture_span()
@app.action("no_results_followup")
def handle_no_results_followup(ack, body, say, payload, logger):
    '''
    When there are no results found, send back the advanced search box
    '''
    apmClient.begin_transaction(transaction_type="handle_no_results_followup")

    ack()
    logger.info('starting no_results_followup')
    logger.info(body)

    text = searchMessagesAdvanced(body, es)

    logging.debug('sending back %s' % text)

    say(text='test',
       blocks = text
       )

    apmClient.end_transaction(name=__name__, result="success")



@elasticapm.capture_span()
@app.action("advanced_search_enable")
def handle_advanced_search_enable(ack, body, say, logger):
    '''
    send back advanced search box
    '''
    #TODO is this still used?
    ack()
    logging.info('starting advanced_search_enable')
    logger.debug(body)

    advSearchBox = buildAdvancedSearchBlock()

    say(text='test',
       blocks = advSearchBox
       )

@elasticapm.capture_span()
@app.action("advanced_submit")
def handle_advanced_submit(ack, body, say, logger):
    '''
    Handle advanced search query
    '''
    apmClient.begin_transaction(transaction_type="advanced_sumbit")

    ack()
    logger.info('Starting advanced_submit')
    logger.info(body)

    slackSearch, docsSearch, blogsSearch  = parseAdvSearchOptions(body)

    results = {
        'slack' : {
            'title' : 'Saved Message Search Results',
            'terms' : slackSearch,
            'results' : False,
            #'blocks' : False
        },
            'docs' : {
            'title' : 'Elastic Docs Search Results',
            'terms' : docsSearch,
            'results' : False,
            #'blocks' : False
        },
            'docs' : {
            'title' : 'Elastic Blogs Search Results',
            'terms' : blogsSearch,
            'results' : False,
            #'blocks' : False
        }
    }

    #TODO possibly have a flag to pull back only the results?
    logging.debug('Advanced Results:')
    logging.debug(results)
    if slackSearch:
        results['slack']['results'] = searchMessages(es=es, searchTermRebuilt=slackSearch )
    if docsSearch:
        results['docs']['results'] = searchDocs(appSearch=appsearch, query = docsSearch)
    if blogsSearch:
        results['docs']['results'] = searchBlogs(appSearch=appsearch, query = docsSearch)


    logging.info('calling combineBlocks')
    logging.debug(results)
    resultsBlock = combineBlocks(results)
    logging.debug('done with combining results')
    logging.debug(resultsBlock)

    say(text='test',
        blocks = resultsBlock
        )

    apmClient.end_transaction(name=__name__, result="success")


# handle secondard form clicks
@elasticapm.capture_span()
@app.action("checkboxes-action")
def handle_checkboxes(ack, body, logger):

    apmClient.begin_transaction(transaction_type="handle_checkboxes")

    ack()
    logger.info('Handling checkboxes-action')
    logger.info(body)

    apmClient.end_transaction(name=__name__, result="success")


# handle secondary form submit
@elasticapm.capture_span()
@app.action("sub-tags_submit")
def handle_sub_tags(ack, body, respond, logger):

    apmClient.begin_transaction(transaction_type="handle_sub_tags")

    logger.info('Handling sub-tags_submit')
    logger.info(body)

    ack()

    # Delete second level tag form
    respond( response_type= 'ephemeral',
        text= 'Thanks for helping tag this content!',
        replace_original = True,
        delete_original = True
    )


    sub_tags = []
    for selection in body['state']['values']['check_box']['checkboxes-action']['selected_options']:
        sub_tags.append(selection['value'])

    ori_ts = body['actions'][0]['value']

    logging.debug('sub tags: %s' % sub_tags)

    # Update tag in es
    logger.info('Calling esUpdateTag')
    esUpdateTag(es, sub_tags, ori_ts, sub=True)

    apmClient.end_transaction(name=__name__, result="success")


# Top Level catagories form response
@elasticapm.capture_span()
@app.action("top_level_tags")
def handle_top_level_tags(ack, body, say, client, respond, logger):

    apmClient.begin_transaction(transaction_type="handle_top_level_tags")


    logger.info('top_level_tags action received')
    logger.info(body)
    pprint(body)

    ack()

    # Delete top level tag form
    respond( response_type= 'ephemeral',
    text= '',
    replace_original = True,
    delete_original = True
    )


    ori_ts = float(body['actions'][0]['block_id'])
    cat_selected = body['actions'][0]['selected_option']['value']
#    cat_selected = body['actions'][0]['selected_option']['text']['text']
    tags_channel = body['channel']['id']
    tags_user = body['user']['id']


#    client.chat_postEphemeral(
#        channel=tags_channel,
#        user=tags_user,
#        text=':bob: Copy That -> category _%s_ selected for original message with ts of _%s_' % (cat_selected, ori_ts)
#    )


    # Update tag in es
    logger.info('Calling esUpdateTag')
    esUpdateTag(es, cat_selected, ori_ts)


    # Send secondary tag form
    secondTagForm = buildSecondaryTags(cat_selected, ori_ts)
    if secondTagForm:
        client.chat_postEphemeral(
            channel=tags_channel,
            user=tags_user,
            text=f"<@{tags_user}> One more question to help organize this info...",
            blocks = secondTagForm
        )
    else:
        client.chat_postEphemeral(
            channel=tags_channel,
            user=tags_user,
            text=f"Thanks for saving the content. We will review and see if we need a new tag selection!"
        )


    apmClient.end_transaction(name=__name__, result="success")


@elasticapm.capture_span()
@app.event("reaction_added")
def store_useful_info(event, payload, say, context: BoltContext, client: WebClient, logger: logging.Logger):

    apmClient.begin_transaction(transaction_type="store_useful_info")

    logger.info('Processing event - reaction_added')
    logger.debug(event)

    # Only want to trigger on specific reaction
    #if event['reaction'] != 'sa-save':
    if event['reaction'] != 'sabot':
        logger.debug('skipping reaction: %s' % event['reaction'])
        return


    # message ts to save / workwith
    ori_msg_ts = event['item']['ts']
    msg_channel = event['item']['channel']

    # Send back reaction to ack
    client.reactions_add(
        #name="wave",
        #name="bob-dark",
        name="sabot",
        channel=event['item']['channel'],
        timestamp=event['item']['ts']
    )

    # Get user to catagorize the message
    topics_form = buildTagsForm(ori_msg_ts)
    slack_user_id = payload["user"]

    client.chat_postEphemeral(
        channel=msg_channel,
        user=slack_user_id,
        text=f"Howdy <@{slack_user_id}> Help others find this content in the future...",
        blocks = topics_form
    )


    ## Find original message
    # ID of channel that the message exists in
    conversation_id = event['item']['channel']

    try:
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
            'message' : message['text'],
            'tags' : {}
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

        #TODO this no longer needs to be broken out
        try:
            payload['message_timestamp'] = event['item']['ts']
            payload['message_ts'] = int(float(event['item']['ts']))
            payload['reaction_ts'] = int(float(event['event_ts']))

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


        ### TODO maybe break out to a function?
        # post to discourse
        logging.debug('payload - %s' % payload)
        dpayload ={
                'title': payload['message'][:51],
                'raw':payload['message'] + 'From: %s - %s' % (payload['real_name'], payload['slack_link'])
                }
        logging.debug('DISCOURSE PAYLOAD - %s' % dpayload)
        dResponse = createTopic(dpayload, discourse_api, discourse_user, discourse_server)


        # Add discourse info
        payload['discourse'] = {
            'id' : dResponse['id'],
            'slug' : dResponse['topic_slug']
        }

        # index doc in es
        logging.debug('payload built - %s' % payload)
        resp = esInsert(es, payload)




        ## Respond to slack with url for Discourse post
        #try:
        #    postURL = '%s/t/%s' % (discourse_server,dResponse['topic_slug'])
        #    client.chat_postEphemeral(
        #        channel=msg_channel,
        #        user=slack_user_id,
        #        text="Your post has been saved to Discourse - %s" % postURL
        #    )
        #except KeyError as e:
        #    logging.error('Error getting Discourse url - %s' % e)
        #    pass
        #    #todo return that there was an error posting

        apmClient.end_transaction(name=__name__, result="success")


    except SlackApiError as e:
        print(f"Error: {e}")
        apmClient.end_transaction(name=__name__, result="failure")

	#TODO send back sad failed reaction or something




## download file/screenshot attachments
# message[files] =[ {'url_private_download': 'https://files.slack.com/files-pri/T03P97LMYGY-F03NB53GKJB/download/blue_duck.png', {}...] }







if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s', level=logging.INFO)
    logging.info('Starting up')

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


