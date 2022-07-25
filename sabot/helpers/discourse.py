import requests
import logging

from pprint import pprint

def discourseConnect(apiKey, apiUsername, server):
    '''Create connection to discourse'''

    pass


def createTopic(payload, apiKey, apiUsername, server):
    '''Post new Topic
    Will clean this up if we move forward

    payload dict:
        'title' :string (will auto shortened to 50 chars)
        'raw' : message body

    url = https://discourse-server.com
    '''


    headers = {
            'Api-Key' : apiKey,
            'Api-Username' : apiUsername
            }

    params = {
            'title' : payload['title'][:51],
            'raw': payload['raw'],
            'category' : 5
            }

    logging.debug('params - %s' % params)

    url = server + '/posts'

    resp = requests.post(url=url, headers=headers, params=params)

    print(resp)
    pprint(resp.json())
    return resp.json()

if __name__ == '__main__':
    pass
