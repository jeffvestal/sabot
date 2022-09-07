from elasticsearch import Elasticsearch, helpers
from elastic_enterprise_search import AppSearch



# Now call API methods
#app_search.search(...)

import logging


def esConnect(cid, user, passwd):
    '''Connect to Elastic Cloud cluster'''

    #TODO switch to API key?
    logging.info('Starting to create ES Connection')
    logging.debug('%s - %s - %s' % (cid, user, passwd))
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))

    logging.info('Finished creating ES Connection')
    return es


def esAppSearchConnect(url, apiKey):
    '''
    Connect to App Search
    '''

    app_search = AppSearch(url, bearer_auth=apiKey)

    return app_search

def generateVector(es, searchText):
    '''
    generate vector to use for search
    '''
    pass

def esInsert(es, payload, index='sabot-slack'):
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
    logging.info('Finished inserting message to ES')


def esUpdateTag(es, tag, ts, index='sabot-slack', sub=False):
    '''
    add a tag to es doc
    '''
    logging.info('Starting esUpdateTag')

    top_sub = 'tags.sub' if sub else 'tags.primary'
    if type(tag) != list:
        tag = [tag]

    update = {
        "query": {
            "bool": {
                "filter": [{
                    "match_phrase": {
                        "message_timestamp": "%s" % ts
                    }
                }]
            }
        },
        "script": {
            "source":
            """
                ctx._source.%s = %s
            """ % (top_sub, tag),
            "lang":
            "painless"
        }
    }

    resp = es.update_by_query(body=update, index=index)

    logging.info('esUpdate complete: %s' % resp)


def esUpdateDiscourseInfo(es, d_id, slug, ts, index='sabot-slack'):
    '''
    add the id and post slug (path) to es
    id can be later used to update the discourse post
    '''
    update = {
        "query": {
            "bool": {
                "filter": [{
                    "match_phrase": {
                        "message_ts.keyword": "%s" % ts
                    }
                }]
            }
        },
        "script": {
            "source":
            """
                ctx._source.discourse = [:];
                ctx._source.discourse.id = %s;
                ctx._source.discourse.slug = "%s"
            """ % (d_id, slug),
            "lang":
            "painless"
        }
    }

    resp = es.update_by_query(body=update, index=index)


def listTags(es, index='sabot-slack'):
    '''
    Provide a list of tags currently used with saved messages
    '''

    logging.info('Starting listTags')

    # TODO it is probably pointless to have primary and sub tags separate.....
    query = {
        "size": 0,
        "aggs": {
            "tags-primary": {
                "terms": {
                    "field": "tags.primary",
                    "size": 100
                }
            },
            "tags-sub": {
                "terms": {
                    "field": "tags.sub",
                    "size": 100
                }
            }
        }
    }

    logging.info('searching ES for tags')
    resp = es.search(index=index, body=query)

    tags = []
    for t in resp['aggregations']:
        for bucket in resp['aggregations'][t]['buckets']:
            tags.append(bucket['key'])

    tag_list = '* ' + '\n * '.join(sorted(tags))

    return tag_list


def buildResultsBlock(urls):
    '''
    Breaking out building the response block
    '''
    logging.info('Starting buildResultsBlock')

    text = ''.join(
        ['<%s|%s> | ' % (url, num + 1) for num, url in enumerate(urls)])

    results = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*`These are the top 5 results I found from saved Slack messages`*"
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Need more results or try something else:"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Advanced Search",
                "emoji": True
            },
            "value": "advanced_search_enable",
            "action_id": "advanced_search_enable"
        }
    }, {
        "type": "divider"
    }]

    return results


def buildNoResultsBlock():
    '''
    when there are no search results
    provide a quick way to do a follow up search
    '''

    noHits = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":thinking_face: I wasn't able to find any matches"
        }
    }, {
        "type": "divider"
    }, {
        "type": "input",
        "block_id": "search_input",
        "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input-action"
        },
        "label": {
            "type": "plain_text",
            "text": "Try a different search",
            "emoji": True
        }
    }, {
        "type":
        "actions",
        "elements": [{
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Go Find It!",
                "emoji": True
            },
            "action_id": "no_results_followup",
            "value": "search_submit"
        }]
    }]

    return noHits


def buildAdvancedSearchBlock(addNoResults=False):
    '''
    Advanced search options
    '''

    logging.info('Starting buildAdvancedSearchBlock')

    #TODO seet end date to TODAY

    if addNoResults:
        advSearchBox = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":thinking_face: I wasn't able to find any matches"
            }
        }, {
            "type": "divider"
        }]
    else:
        advSearchBox = []

    advSearchBox.extend([
        {
            "type": "divider"
        },
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Advanced Search",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "input",
            "block_id": "text_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "plain_text_input-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Words or phrase (uses multi_match) [*required]",
                "emoji": True
            }
        },
        #{
        #    "type": "divider"
        #},
        #{
        #    "type": "section",
        #    "text": {
        #        "type": "plain_text",
        #        "text": "Select a date range to search (slack).",
        #        "emoji": True
        #    }
        #},
        #{
        #    "type":
        #    "actions",
        #    "elements": [
        #        {
        #           "type": "datepicker",
        #            "initial_date": "2010-02-08",
        #            "placeholder": {
        #                "type": "plain_text",
        #                "text": "Select a date",
        #                "emoji": True
        #            },
        #            "action_id": "date_start"
        #        },
        #        {
        #            "type": "datepicker",
        #            "initial_date": "1990-04-28",  #set to toay
        #            "placeholder": {
        #                "type": "plain_text",
        #                "text": "Select a date",
        #                "emoji": True
        #            },
        #            "action_id": "date_end"
        #        }
        #    ]
        #},
        {
            "type": "section",
            "block_id": "search_selections",
            "text": {
                "type": "mrkdwn",
                "text": "Where should I search:"
            },
            "accessory": {
                "type":
                "checkboxes",
                "initial_options": [{
                    "text": {
                        "type": "mrkdwn",
                        "text": "Search saved slack messages"
                    },
                    "value": "search_slack"
                }],
                "options": [
                    {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Search saved slack messages"
                    },
                    "value": "search_slack"
                },
                    {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Search elastic.co docs"
                    },
                    "value": "search_docs"
                },
                                        {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Search elastic.co Blogs"
                    },
                    "value": "search_blogs"
                }
                           ],
                "action_id":
                "checkboxes-action"
            }
        },
        {
            "type":
            "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Go Find It!",
                    "emoji": True
                },
                "action_id": "advanced_submit",
                "value": "search_submit"
            }]
        }
    ])

    return advSearchBox


def buildDocsBlock(resp):
    '''
    build out docs results
    '''

    logging.info('starting buildDocsBlock')
    logging.debug(resp)

    docs = ''
    for d in resp:
        docs = docs + '<%s|%s>\n' % (d['url']['raw'], d['title']['raw'])

    docsResults = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*`These are the top results I found from Elastic Docs`*"
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": docs
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Need more results or try something else:"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Advanced Search"
            },
            "value": "advanced_search_enable",
            "action_id": "advanced_search_enable"
        }
    }]

    return docsResults



def buildBlogsBlock(resp):
    '''
    build out docs results
    '''

    logging.info('starting buildBlogsBlock')
    logging.debug(resp)

    docs = ''
    for d in resp:
        docs = docs + '<%s|%s>\n' % (d['url']['raw'], d['title']['raw'])

    docsResults = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*`These are the top results I found from Elastic Blogs`*"
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": docs
        }
    }, {
        "type": "divider"
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Need more results or try something else:"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Advanced Search"
            },
            "value": "advanced_search_enable",
            "action_id": "advanced_search_enable"
        }
    }]

    return docsResults



def searchMessages(payload=False, es=False, searchTermRebuilt=False, index='sabot-slack'):
    '''
    Searching for saved messages
    '''

    logging.info('Starting searchMessages')

    if searchTermRebuilt:
        logging.info('search term provided directly')
    else:
        logging.info('parsing out search term from payload')
        logging.debug(payload)
        searchTerms = payload['text'].split()[2:]
        searchTermRebuilt = ' '.join(searchTerms)
        if searchTermRebuilt.lower().strip() == 'advanced':
            return 'advanced search coming soon'


    esBody = {
            "size": 5,
            "query": {
                "bool": {
                    "must": [{
                        "multi_match": {
                            "type": "best_fields",
                            "query": "%s" % searchTermRebuilt,
                            "lenient": True
                        }
                    }]
                }
            }
        }

    logging.info('searching ES "%s"' % esBody)
    resp = es.search(index=index, body=esBody)

    if resp['hits']['total']['value'] == 0:
        #        results = buildNoResultsBlock()
        results = buildAdvancedSearchBlock(addNoResults=True)
    else:
        urls = [hit['_source']['slack_link'] for hit in resp['hits']['hits']]
        results = buildResultsBlock(urls)

    return results


def searchMessagesAdvanced(body, es, index='sabot-slack'):
    '''
    handle advanced search box
    '''

    logging.info('starting searchMessagesAdvanced')
    logging.debug(body)
    searchString = body['state']['values']['search_input'][
        'plain_text_input-action']['value']

    esBody = {
        "size": 5,
        "query": {
            "bool": {
                "must": [{
                    "multi_match": {
                        "type": "best_fields",
                        "query": "%s" % searchString,
                        "lenient": True
                    }
                }]
            }
        }
    }

    logging.info('searching ES "%s"' % esBody)
    resp = es.search(index=index, body=esBody)

    if resp['hits']['total']['value'] == 0:
        logging.info('no results found')
        results = buildNoResultsBlock()
    else:
        logging.info('processing results')
        urls = [hit['_source']['slack_link'] for hit in resp['hits']['hits']]
        results = buildResultsBlock(urls)

    return results


def searchDocs(payload=False, rest=False, appSearch=False, query=False):
    '''
    Search elastic.co docs
    '''

    logging.info('starting searchDocs')

    if query:
        logging.info('query provided')
    else:
        logging.debug(payload)
        logging.debug(rest)
        query = ' '.join(rest)

    resp = appSearch.search(engine_name="elastic-guide-docs",
                                body={"query": query,
                                      "result_fields": {
                                        "title": {
                                            "raw": {}
                                        },
                                        "url": {
                                            "raw": {}
                                        }
                                     }
                                     }
                            )

    results = buildDocsBlock(resp['results'])

    logging.debug(results)

    return results


def searchBlogs(payload=False, rest=False, appSearch=False, query=False):
    '''
    Search elastic.co docs
    '''

    logging.info('starting searchBlogs')

    if query:
        logging.info('query provided')
    else:
        logging.debug(payload)
        logging.debug(rest)
        query = ' '.join(rest)
    # result_fields
    resp = appSearch.search(engine_name="elastic-blogs",
                                body={"query": query,
                                      "result_fields": {
                                        "title": {
                                            "raw": {}
                                        },
                                        "url": {
                                            "raw": {}
                                        }
                                     }
                                     }
                            )

    #TODO split out to separate blocks builder - maybe
    results = buildBlogsBlock(resp['results'])

    logging.debug('searchBlogs results')
    logging.debug(results)

    return results


if __name__ == '__main__':
    logging.basicConfig(
        format=
        '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s',
        level=logging.INFO)

#vim: expandtab tabstop=4
