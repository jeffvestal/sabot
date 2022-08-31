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

## Example Usage
### Tagging a message
When you tag a message with `sabot` response
1. `@sabot` will also use the same response to ack it
2. you will get a popup, only visable to you, asking to help categorize the message
<img width="715" alt="CleanShot 2022-08-31 at 13 42 32@2x" src="https://user-images.githubusercontent.com/53237856/187759391-7c0b76c9-e344-4341-89d1-f3fb3d996c64.png">

3. Second level categorization popup

<img width="698" alt="CleanShot 2022-08-31 at 13 42 45@2x" src="https://user-images.githubusercontent.com/53237856/187759728-84b2b39c-e548-4148-8b28-1b4eb5d555f9.png">

<img width="681" alt="CleanShot 2022-08-31 at 13 42 59@2x" src="https://user-images.githubusercontent.com/53237856/187760510-34ea1fbf-825b-4f33-8c9d-159f0a9c40bd.png">


### Searching
The easiest way to search is with `@sabot search <search terms>`

This will search previously searched slack messages, Elastic Docs, and Elastic Blogs. 

You can search any of those individually with the specific command `slack`, `docs`, or `blogs` followed by the search terms

<img width="548" alt="CleanShot 2022-08-31 at 13 44 53@2x" src="https://user-images.githubusercontent.com/53237856/187760530-3ca02e06-249a-415a-8456-52c99c2f725e.png">

<img width="838" alt="CleanShot 2022-08-31 at 13 45 23@2x" src="https://user-images.githubusercontent.com/53237856/187760567-498b3ebc-36dd-4534-875f-0eac8d259d70.png">

<img width="820" alt="CleanShot 2022-08-31 at 13 45 36@2x" src="https://user-images.githubusercontent.com/53237856/187760604-c9559cfc-5ce9-4824-82d3-19f7a16f2e62.png">

## Example video

https://user-images.githubusercontent.com/53237856/187762232-60b35362-bbaa-4f5d-8d85-ea06ce8765de.mp4


# Environment Variables that must be set

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
