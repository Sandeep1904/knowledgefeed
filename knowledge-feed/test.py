from main import FeedBuilder, FeedModifier
import json


user_input = 'spectral graph theory'
query_type = 'academic'
newFeed = FeedBuilder().build_feed(user_input, query_type)

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
