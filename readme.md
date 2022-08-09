# SA Bot
Jeff Vestal

A bot that saves slack messages when an emoji is triggered
Also provides search of saved messages, and app search engines
Maybe some other stuff at some point

## Help Output
> Hi There!, I know how to do the following:
> 
> Saving Slack Messages
> 
> When you see a message in Slack you think is useful, helpful, or worth
> saving   for easy retrieval in the future:   Tag any message with the 
> :sa-save:  reaction
> 
> You will get sent back a message asking for your help tagging the
> message, to make it easier to find in the future

> 
> Commands I understand
> 
> `help`  - You are reding this now
> 
> `search [search terms]`  - Search for previously saved Slack Messages
> 
> `docs [search terms]`  - Search Elastic Docs
> 
> `search advanced`  - Bring up the advanced search form
> 
> `listtags`  - List tags of previously saved Slack messages

## Environment Variables that must be set

- "sabot_cloud_id": <ess_cloud_id>
- "sabot_cloud_es_user": "<ess_user>"
- "sabot_cloud_es_pass": "<ess_user_password>"
- "discourse_user": "<discourse_user>"
- "discourse_api": "<discourse_bot_api>"
- "discourse_server": "<discourse_url>
-   "SLACK_APP_TOKEN": "<slack_app_token>"
-  "SLACK_BOT_TOKEN": "<slack_bot_token>"
- "sabot_appsearch_api": "<ess_app_search_api>"
- "sabot_appsearch_url": "<ess_app_search_url>"
- "ELASTIC_APM_SECRET_TOKEN": "<ess_apm_token>"
- "ELASTIC_APM_SERVICE_NAME": "<ess_app_name>"
- "ELASTIC_APM_SERVER_URL": "<_ess_apm_server_url>"