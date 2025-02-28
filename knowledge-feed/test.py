from main import FeedBuilder
import json


user_input = 'Google'
newFeed = FeedBuilder().build_feed(user_input)

file_name = 'output.json'

with open(file_name, 'w') as json_file:
    json.dump(newFeed, json_file, indent=4)

# lets test the modifications now
