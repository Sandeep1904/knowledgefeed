from main import FeedBuilder, FeedModifier
import json


user_input = 'multi head attention'
query_type = 'academic'
newFeed = FeedBuilder().build_feed(user_input, query_type, start =0)

# for you to see the output
file_name = 'output.json'

with open(file_name, 'w') as json_file:
    json.dump(newFeed, json_file, indent=4)

# lets test the modifications now
# with open('output.json') as json_file:
#     newFeed = json.load(json_file)

# modifier = FeedModifier()


# modifiedpostFeed = modifier.modify_chatContext(newFeed, 5, 0, 'This is the new chat context')


# file_name = 'modifiedchatcontext.json'

# with open(file_name, 'w') as json_file:
#     json.dump(modifiedpostFeed, json_file, indent=4)


# modifiedagentFeed = modifier.modify_agent(newFeed, 0, 'claude', 'groq', '0.1', 'crazy')

# file_name = 'modifiedagent.json'

# with open(file_name, 'w') as json_file:
#     json.dump(modifiedagentFeed, json_file, indent=4)

# sample json response.
[
    {
        "objecID": 0,
        "abslink": "abc",
        "pdflink": "abc",
        "md_str": "abc",
        "agent": [
            {
                "model": "abc",
                "source": "abc",
                "personality": "abc",
                "temperature": 0,
            }
        ],
        "posts": [
            {
                "postID": 0,
                "text": "abc",
                "chatContext": "abc",
                "resources": [
                    {
                    "images": [
                        {
                            "title": "abc",
                            "image": "https://abc",
                        }
                    ],
                    "videos": [
                        {
                            "title": "abc",
                            "video": "https://abc",
                        }
                    ],
                    "newsArticles": [
                        {
                            "title": "abc",
                            "url": "https://abc",
                        }
                    ],
                    }
                ],
            
            }
        ],
    }
]


# stream instead of batch
# load more not working
# character change config with Feed modifier
# comment UI agent reply
# bot icon as author


# avoid state refresh after clicked

