import random
import sys
import json
from duckduckgo_search import DDGS


md_str = """
UUIDs (Universally Unique Identifiers) are designed to be unique across space and time, and they achieve this through several methods depending on the version of UUID being used. Here are the key points explaining how UUIDs can be unique without tracking previous generations:

1. **Randomness**: Many UUID versions (like UUID4) generate IDs using random numbers. The probability of generating the same random number twice is extremely low due to the vast number of possible combinations (2^122 for UUID4).

2. **Time and MAC Address**: Other versions (like UUID1) combine the current timestamp with the MAC address of the machine generating the UUID. This ensures that even if two UUIDs are generated at the same time, they will be unique due to the different MAC addresses.

3. **Namespace and Name**: UUID5 and UUID3 generate IDs based on a namespace and a name using hashing (SHA-1 for UUID5 and MD5 for UUID3). This means that the same input will always produce the same UUID, but different inputs will produce different UUIDs.

4. **Collision Resistance**: The design of UUIDs takes into account the likelihood of collisions. With a sufficiently large space (like 128 bits), the chance of generating the same UUID is astronomically low, making it practically unique.

In summary, UUIDs use a combination of randomness, time, machine identifiers, and hashing to ensure uniqueness without needing to track previously generated UUIDs.
"""

class Feed:
    existing_ids = set() 

    def randidgenerator(self):
        unique_id = random.randint(10000, 99999)  
        if unique_id not in self.existing_ids:
            self.existing_ids.add(unique_id)
            return unique_id


    def __init__(self, abslink, pdflink, md_str):
        self.abslink = abslink
        self.pdflink = pdflink
        self.md_str = md_str
        self.id = self.randidgenerator()
        self.items = {
            'id': self.id,
            'abslink': self.abslink,
            'pdflink': self.pdflink,
            'md_str': self.md_str,
        }

    def add_agent(self, agent):
        self.items.update({'agent': agent})
        sys.stdout.write('Agent added successfully!\n')

    def add_posts(self, posts):
        self.items.update({'posts': posts})
        sys.stdout.write('Posts added successfully!\n')

    def get_feed(self):
        return self.items
    

class Agent:

    def __init__(self, model, source, temp, personality):
        self.model = model
        self.source = source    
        self.temp = temp
        self.personality = personality
        self.agent = {
            'model': self.model,
            'source': self.source,
            'temp': self.temp,
            'personality': self.personality,
        }

    def get_agent(self):
        return self.agent
    

class Posts:
    
    def __init__(self):
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)
        sys.stdout.write('Post added successfully!\n')

    def get_posts(self):
        return self.posts


class Post:

    existing_ids = set() 

    def randidgenerator(self):
        unique_id = random.randint(10000, 99999)  
        if unique_id not in self.existing_ids:
            self.existing_ids.add(unique_id)
            return unique_id

    def __init__(self, text, chatContext, resources):
        self.text = text
        self.chatContext = chatContext
        self.resources = resources
        self.id = self.randidgenerator()
        self.resources = resources
        self.post = {
            'id': self.id,
            'text': self.text,
            'chatContext': self.chatContext,
            'resources': self.resources,
        }

    def get_post(self):
        return self.post
    

class Modifier:

    def __init__(self, context):
        pass


class Builder:

    def __init__(self):
        pass

    def build_posts(self, md_str, resources={}):
        self.md_str = md_str
        self.recources = resources
        posts = Posts()
        results = DDGS().chat("Chunk this text into meaningful parts and only return a list object: UUIDs (Universally Unique Identifiers) are designed to be unique across space and time, and they achieve this through several methods depending on the version of UUID being used. Here are the key points explaining how UUIDs can be unique without tracking previous generations:\n\n1. **Randomness**: Many UUID versions (like UUID4) generate IDs using random numbers. The probability of generating the same random number twice is extremely low due to the vast number of possible combinations (2^122 for UUID4).\n\n2. **Time and MAC Address**: Other versions (like UUID1) combine the current timestamp with the MAC address of the machine generating the UUID. This ensures that even if two UUIDs are generated at the same time, they will be unique due to the different MAC addresses.\n\n3. **Namespace and Name**: UUID5 and UUID3 generate IDs based on a namespace and a name using hashing (SHA-1 for UUID5 and MD5 for UUID3). This means that the same input will always produce the same UUID, but different inputs will produce different UUIDs.\n\n4. **Collision Resistance**: The design of UUIDs takes into account the likelihood of collisions. With a sufficiently large space (like 128 bits), the chance of generating the same UUID is astronomically low, making it practically unique.\n\nIn summary, UUIDs use a combination of randomness, time, machine identifiers, and hashing to ensure uniqueness without needing to track previously generated UUIDs.", model='gpt-4o-mini')
        
        try:
            sentences = json.loads(results)
            for i, sentence in enumerate(sentences):
                post = Post(sentence, md_str, resources)
                posts.add_post(post.get_post())

        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON: {e}")

        # print(posts.get_posts())
        return posts

    def build_feed(self, abslink, pdflink, md_str, model, source, temp, personality):
        feed = Feed(abslink, pdflink, md_str)
        agent = Agent(model, source, temp, personality)
        feed.add_agent(agent.get_agent())
        
        posts = self.build_posts(md_str)
        
        feed.add_posts(posts.get_posts())
        sys.stdout.write('Feed built successfully!\n')
        return feed.get_feed()
        

my_feed = Builder().build_feed('https://example.com', 'https://example.com/pdf', md_str, 'gpt-4o-mini', 'ddgs', 'medium', 'nerdy')
print(json.dumps(my_feed, indent=4))