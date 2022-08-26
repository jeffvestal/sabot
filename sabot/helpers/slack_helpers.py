import logging

def buildTagsForm(ts):
    '''
    build out the form blocks allowing a user to select a tag
    to better catagorize the saved message

    Right now it just returns the set form
    '''

    top_level_tags = [{
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "Help organize this useful message so others can find it",
            "emoji": True
        }
    }, {
        "type": "section",
        "block_id": ts,
        "text": {
            "type": "mrkdwn",
            "text": "Select the most appropriate category tag"
        },
        "accessory": {
            "type":
            "radio_buttons",
            "options": [{
                "text": {
                    "type": "plain_text",
                    "text": "Enterprise Search",
                    "emoji": True
                },
                "value": "search"
            }, {
                "text": {
                    "type": "plain_text",
                    "text": "Observability",
                    "emoji": True
                },
                "value": "observability"
            }, {
                "text": {
                    "type": "plain_text",
                    "text": "Security",
                    "emoji": True
                },
                "value": "security"
            }, {
                "text": {
                    "type": "plain_text",
                    "text": "Platform",
                    "emoji": True
                },
                "value": "platform"
            }, {
                "text": {
                    "type": "plain_text",
                    "text": "Needs Review (none of these fit)",
                    "emoji": True
                },
                "value": "needs_review"
            }],
            "action_id":
            "top_level_tags"
        }
    }]

    return top_level_tags



def buildSecondaryTags(topTag, ts):
    '''
    return a form getting input for second level tags
    based on what the top level tag was
    '''

    if topTag == 'observability':
        o11y_sub_tags = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Based on your selection of the tag:Observability"
            }
        }, {
            "type": "section",
            "block_id": "check_box",
            "text": {
                "type": "mrkdwn",
                "text": "This is a section block with checkboxes."
            },
            "accessory": {
                "type":
                "checkboxes",
                "options": [{
                    "text": {
                        "type": "mrkdwn",
                        "text": "APM"
                    },
                    "value": "apm"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Logs"
                    },
                    "value": "logs"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Metrics"
                    },
                    "value": "metrics"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Uptime"
                    },
                    "value": "uptime"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Needs Review (None of these fit)"
                    },
                    "value": "o11y-needs_review"
                }],
                "action_id":
                "checkboxes-action"
            }
        }, {
            "type": "divider"
        }, {
            "type":
            "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Update Tags"
                },
                "action_id": "sub-tags_submit",
                "value": "%s" % ts
            }]
        }]
        return o11y_sub_tags

    elif topTag == 'security':
        security_sub_tags = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Based on your selection of the tag:Security"
            }
        }, {
            "type": "section",
            "block_id": "check_box",
            "text": {
                "type": "mrkdwn",
                "text": "This is a section block with checkboxes."
            },
            "accessory": {
                "type":
                "checkboxes",
                "options": [{
                    "text": {
                        "type": "mrkdwn",
                        "text": "SIEM"
                    },
                    "value": "siem"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Endpoint"
                    },
                    "value": "endpoint"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Cloud Security"
                    },
                    "value": "cloud_security"
                }
            ],
                "action_id":
                "checkboxes-action"
            }
        }, {
            "type": "divider"
        }, {
            "type":
            "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Update Tags"
                },
                "action_id": "sub-tags_submit",
                "value": "%s" % ts
            }]
        }]
        return security_sub_tags

    elif topTag == 'search':
        search_sub_tags = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Based on your selection of the tag:Search"
            }
        }, {
            "type": "section",
            "block_id": "check_box",
            "text": {
                "type": "mrkdwn",
                "text": "This is a section block with checkboxes."
            },
            "accessory": {
                "type":
                "checkboxes",
                "options": [{
                    "text": {
                        "type": "mrkdwn",
                        "text": "Elasticsearch"
                    },
                    "value": "elasticsearch"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "App Search"
                    },
                    "value": "app_search"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Workplace Search"
                    },
                    "value": "workplace_search"
                }
            ],
                "action_id":
                "checkboxes-action"
            }
        }, {
            "type": "divider"
        }, {
            "type":
            "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Update Tags"
                },
                "action_id": "sub-tags_submit",
                "value": "%s" % ts
            }]
        }]
        return search_sub_tags

    elif topTag == 'platform':
        platform_sub_tags = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Based on your selection of the tag:Platform"
            }
        }, {
            "type": "section",
            "block_id": "check_box",
            "text": {
                "type": "mrkdwn",
                "text": "This is a section block with checkboxes."
            },
            "accessory": {
                "type":
                "checkboxes",
                "options": [{
                    "text": {
                        "type": "mrkdwn",
                        "text": "Cloud"
                    },
                    "value": "cloud"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "ECE"
                    },
                    "value": "ece"
                }, {
                    "text": {
                        "type": "mrkdwn",
                        "text": "ECK"
                    },
                    "value": "eck"
                }
            ],
                "action_id":
                "checkboxes-action"
            }
        }, {
            "type": "divider"
        }, {
            "type":
            "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Update Tags"
                },
                "action_id": "sub-tags_submit",
                "value": "%s" % ts
            }]
        }]
        return platform_sub_tags

    else:
        return False


def parseCommands(payload):
    '''
    parse out the command that the bot is being asked to do
    '''


    splitUp = payload['text'].split()
    command, rest = splitUp[1], splitUp[2:]

    return command, rest

def helpCommands():
    '''
    list of commands the bot understands
    '''

    #help = '''
    #I knows how to do the following:
    #Format is `@sabot <command> [optional inputs]`

    #`help` --> You are reading it now
    #`listtags` --> List the tags that have been added to messages
    #`search` [search terms] --> search for [search terms]. leave blank for adv search form

    #-> More to come!
    #-> Any issues reach out to `@vestal`
    #'''

    help =  [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Hi There!, I know how to do the following:",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Saving Slack Messages",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "When you see a message in Slack you think is useful, helpful, or worth saving\nfor easy retrieval in the future:\nTag any message with the :sabot: `:sabot:` reaction"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "You will get sent back a message asking for your help tagging the message, to make it easier to find in the future"
			}
		},
		{
			"type": "divider"
		},
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "I can search content from:",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "* Previously saved slack messages\n* Elastic Docs\n* Elastic Blogs",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Commands I understand",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`help` - You are reding this now"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`search [search terms]` - Search previously saved slack messages, docs, and blogs"
			}
		},
   		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`slack [search terms]` - Search for previously saved Slack Messages"
			}
		},

		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`docs [search terms]` - Search Elastic Docs"
			}
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`blogs [search terms]` - Search Elastic Blogs"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "`advanced` - Bring up the advanced search form"
			}
		},
#	{
#			"type": "section",
#			"text": {
#				"type": "mrkdwn",
#				"text": "`listtags` - List tags of previously saved Slack messages"
#			}
#		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Any issues/request reach out to `@vestal` or <https://github.com/jeffvestal/sabot/issues|open a GH Issue>"
				}
			]
		}
	]

    return help

def advancedHelp():


    advBox = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: Enter search info below"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Search Terms",
				"emoji": True
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Go Find It!",
						"emoji": True
					},
                    "action_id": "submit",
					"value": "search_submit"
				}
			]
		}
	]


def parseAdvSearchOptions(body):
    '''
    parse out advanced search options
    for slack and docs
    return False for any that aren't checked

    checkboxes - search_slack, search_docs
    '''

    logging.debug(body)

    searchText = body['state']['values']['text_input']['plain_text_input-action']['value']
    checkBox = [option['value'] for option in body['state']['values']['search_selections']['checkboxes-action']['selected_options']]
    logging.debug('searchText - %s' % searchText)
    logging.debug('checkBox - %s' % checkBox)


    #TODO There is a cleaner way to do this block if we get more options...
    search_slack = searchText if 'search_slack' in checkBox else False
    search_docs = searchText if 'search_docs' in checkBox else False
    search_blogs = searchText if 'search_blogs' in checkBox else False

    return (search_slack, search_docs, search_blogs)


def combineBlocks(results):
    '''
    combine multiple result blocks
    '''
    combined = []
    logging.debug(results)

    for r in results:
        try:
            for block in results[r]['results']:
                combined.append(block)
        except TypeError:
            logging.debug('no results for %s' % r)
            pass

    return combined
