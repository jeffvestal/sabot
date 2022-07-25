from elasticsearch import Elasticsearch, helpers
import logging



def esConnect(cid, user, passwd):
    '''Connect to Elastic Cloud cluster'''

    #TODO switch to API key?
    logging.info('Starting to create ES Connection')
    logging.debug('%s - %s - %s' % (cid, user, passwd))
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))

    logging.info('Finished creating ES Connection')
    return es


def esInsert(es, payload, index='a-team-helicopter' ):
    '''Insert message to ES
    payload :
    {
        'reaction': {
           'user': user,
           'reaction': reaction,
           'channel': item.channel
           'message_ts' : item.ts,
           'event_ts' : event_ts
        }
        'author' : user,
        'message' : text,
        'message_ts' : ts,
        'channel' : item.channel,
        'slack_link' : #Need to construct permalink somehow

        'files': [
		{
		'filetype' : filetype,
		'permalink' : permalink,
		'thumb_800' : thumb_800,
		'title' : title,
		'user': user
		},
	]
    }
    '''

    logging.info('Starting to insert message into ES')
    res = es.index(index=index, body=payload)
    logging.info(res)
    logging.info('Finished inserting rides to ES')




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s', level=logging.INFO)


#vim: expandtab tabstop=4
