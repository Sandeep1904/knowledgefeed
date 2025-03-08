import copy
import sys
import json
import urllib, urllib.request
import xml.etree.ElementTree as ET
from duckduckgo_search import DDGS
from docling.document_converter import DocumentConverter
from openai import OpenAI
import os, requests
import math
from dotenv import load_dotenv

load_dotenv()

key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key = key,
)

groq_client = OpenAI(
    api_key = os.environ['GROQ_API_KEY'],
    base_url = "https://api.groq.com/openai/v1/"
)


class Fetcher:
    def __init__(self):
        pass

    def categoriser(self, query, query_type='business',start=0):
        
        query_type = query_type.lower()
        allContent = []
        converter = DocumentConverter()
        
        if query_type == 'academic':
            query = query.strip().split(' ')
            query = "+".join(query)
            
            url = f'http://export.arxiv.org/api/query?search_query={query}&start={start}&max_results=2'
            try:
                xml_data = urllib.request.urlopen(url).read().decode('utf-8')
                print("Academic data fetch successful")
            except Exception as e:
                print(f"Error fetching data: {e}")
                xml_data = ""

            # Parse the XML data
            if xml_data:
                root = ET.fromstring(xml_data)

                # Define the namespace
                ns = {'atom': 'http://www.w3.org/2005/Atom'}

                # Find all PDF links
                pdf_sources = [link.get('href') for link in root.findall(".//atom:link[@title='pdf']", ns)]

            else:
                print("No XML data to parse.")

            news_sources = DDGS().news(query, max_results=2)
            img_sources = DDGS().images(query, max_results=2)
            video_sources = DDGS().videos(query, max_results=2)
            resources = [
                {
                    'images' : img_sources, # list of objects
                    'videos' : video_sources, # list of objects
                    'newsArticles': news_sources, # list of objects
                }
            ]



            for source in pdf_sources:
                
                md_str = converter.convert(source)
                md_str = md_str.document.export_to_markdown()
                
                # add more to return resources if found
                
                allContent.append({'pdflink': source, 'md_str': md_str, 'resources': resources})

        elif query_type == "testing":
            img_sources = DDGS().images(query, max_results=2)
            resources = [
                {
                'images' : img_sources, # list of objects
            }
            ]
            sources = [
                {
                    "url": "https://purplekicks.com/",
                },
                {
                    "url": "https://suggestanime.streamlit.app/"
                }

            ]
            for source in sources:
                url = source['url']
                response = requests.get(url)
                md_str = str(response.content)
                allContent.append({'abslink': source['url'], 'md_str': md_str, 'resources': resources})


        else:
            news_sources = DDGS().news(query, max_results=2)
            print(f'news sources {news_sources}')
            print("Business data fetch successful")
            img_sources = DDGS().images(query, max_results=2)
            video_sources = DDGS().videos(query, max_results=2)
            resources = [
                {
                'images' : img_sources, # list of objects
                'videos' : video_sources, # list of objects
            }
            ]
            for news in news_sources:
                print(f'news {news}')
                # replace this with processing of news articles
                url = news['url']
                # md_str = converter.convert(url)
                # md_str = md_str.document.export_to_markdown()
                response = requests.get(url)
                md_str = response.content
                allContent.append({'abslink': news['url'], 'md_str': md_str, 'resources': resources})
        print("Returning all content!")
        return allContent
    

class FeedBuilder:
    
    def __init__(self):
        pass

    def build_feed(self, user_input, query_type, start):
        allContent = Fetcher().categoriser(user_input, query_type, start)
        print(allContent)
        feed = []
        for content in allContent:
            
            abslink = content.get('abslink', None)
            pdflink = content.get('pdflink', None)
            md_str = content.get('md_str', None)
            resources = content.get('resources', None)
            model = 'llama-3.3-70b'
            source = 'ddgs'
            temp = 0.7
            personality = 'friendly'
            ob = ObjectBuilder()
            objectResponse = ob.build_object(abslink, pdflink, md_str, model, source, temp, personality, resources)
            feed.append(objectResponse)
            print("Sent OBJECT to frontend")
            yield objectResponse
            
        file_name = 'output.json'

        with open(file_name, 'w') as json_file:
            json.dump(feed, json_file, indent=4)
            print("Feed stored in Json file")



class Feed:
    id = -1

    def __init__(self, abslink, pdflink, md_str):
        self.abslink = abslink
        self.pdflink = pdflink
        self.md_str = md_str
        Feed.id += 1
        self.id = Feed.id
        self.items = {
            'objectID': self.id,
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
        self.agent = [
            {
            'model': self.model,
            'source': self.source,
            'temp': self.temp,
            'personality': self.personality,
        }
        ]

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

    id = -1
    oldobjectID = 0


    def __init__(self, text, chatContext, resources, objectID):
        self.text = text
        self.chatContext = chatContext
        self.resources = resources
        
        self.newobjectID = objectID
        if self.oldobjectID != self.newobjectID:
            Post.oldobjectID = self.newobjectID
            Post.id = -1
        Post.id += 1
        self.id = Post.id
        self.resources = resources
        self.post = {
            'postID': self.id,
            'text': self.text,
            'chatContext': self.chatContext,
            'resources': self.resources,
        }

    def get_post(self):
        return self.post
    

class FeedModifier:
    # return a copy of origianl feed. user can choose to replace.

    def __init__(self):
        pass

    def modify_agent(self, feed, objectID, model, source, temp, personality):
        sys.stdout.write("Old agent: \n")
        sys.stdout.write(str(feed[objectID].get('agent')))
        copyfeed = copy.deepcopy(feed)
        copyfeed[objectID]['agent'].update({
            'model': model,
            'source': source,
            'temp': temp,
            'personality': personality,
        })
        sys.stdout.write(f"\nAfter modifying agent for objectID: {objectID}\n")
        sys.stdout.write(str(copyfeed[objectID].get('agent')))
        return copyfeed

    def modify_chatContext(self, feed, objectID, postID, newchatContext):
        sys.stdout.write("\nOld chatContext: \n")
        sys.stdout.write(str(feed[objectID]['posts'][postID].get('chatContext')))
        copyfeed = copy.deepcopy(feed)
        copyfeed[objectID]['posts'][postID].update({'chatContext': newchatContext})
        sys.stdout.write(f"\nAfter modifying chatContext for objectID: {objectID}, postID: {postID}\n")
        sys.stdout.write(str(copyfeed[objectID]['posts'][postID].get('chatContext')))
        return copyfeed

    


class ObjectBuilder:

    def __init__(self):
        self.model= 'llama-3.3-70b'
        self.source = 'ddgs'

    def break_markdown(md_str, max_length):
        # Initialize an empty list to hold the chunks
        chunks = []
        # Start from the beginning of the string
        start = 0
        percentage = 0.3
        n = len(chunks)

        # Loop until the end of the string
        while start < len(md_str):
            # Get the end index for the current chunk
            end = start + max_length
            
            # If the end index exceeds the string length, adjust it
            if end > len(md_str):
                end = len(md_str)
            
            # Append the chunk to the list
            chunks.append(md_str[start:end])
            
            # Move the start index to the end of the current chunk
            start = end

        remove = math.floor(n*percentage)

        if n - remove > 2:
            start_index = remove
            end_index = n - remove

            return chunks[start_index:end_index]

        return chunks

    def build_posts(self, md_str, resources, objectID):
        self.md_str = md_str
        self.recources = resources
        posts = Posts()
        chunks = ObjectBuilder.break_markdown(md_str, 4000)
        results = ""
        for chunk in chunks:
 
            prompt = f"""You are a deligent research assistant and you have 3 tasks.
            1. Clean the markdown string given below about a academic or business
            topic by removing all unnecessary sections that don't cotribute any 
            insights about the main topic. Must not produce output yet.
            2. Then analyze the cleaned content and create as many caption-sized highlights
            as possible. Must not produce output yet.
            3. Finally, your response should only and only contain a list of strings,
            that are the highlights you created in the previous step.
            {chunk}
        """
        # call a funtion here that handles everything llm related
            # health, self.model, self.source = LLMHandler().check_health(self.model, self.source)
            chunk_results = LLMHandler().call_llm(input=prompt, model=self.model, source=self.source, personality='assistant')
            results = results + chunk_results + "\n"
 
        md_str = results   
        # print(f"mdstr after joining {md_str}")
        # print(f"mdstr after replacing new line char {md_str}")
        # every sentence is empty
        # sentences is not empty but new line char
        # results is series of \n
        # chunk results is empty -> llm output problem or assignment problem
        try:
            sentences = results.split("\n")
            for i, sentence in enumerate(sentences):
                # print(f"this is the current sentence {sentence}")
                post = Post(sentence, md_str, resources, objectID)
                posts.add_post(post.get_post())

        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON: {e}")

        # print(posts.get_posts())
        return posts

    def build_object(self, abslink, pdflink, md_str, model, source, temp, personality, resources):
        feed_object = Feed(abslink, pdflink, md_str)
        agent = Agent(model, source, temp, personality)
        feed_object.add_agent(agent.get_agent())
        
        posts = self.build_posts(md_str, resources, feed_object.id)
        
        feed_object.add_posts(posts.get_posts())
        sys.stdout.write('Object built successfully!\n')
        return feed_object.get_feed()


class LLMHandler():
    def __init__(self):
        self.health = True

    def call_llm(self, input, model, source,  personality, temp=0.7):
        results = ""
        source.lower()
        if source == 'ddgs':
            try:
                results = DDGS().chat(input, model=model)
                # print(f"ddgs gave this result: {results}")
                # print(type(results))
            except Exception as e:
                print(f"ddgs output error: {e}")
                model = "llama-3.3-70b-versatile"
                source = 'groq'
        
        if source == 'groq':
            try:
                results = groq_client.chat.completions.create(
                model=model,
                temperature=temp,

                messages=[
                    {
                        "role": "user",
                        "content": input
                    }
                ],

                )
                results = str(results.choices[0].message.content)
                # print(f"groq gave this result: {results}")
                # print(type(results))
            except Exception as e:
                print(f"groq output error: {e}")
                model = "gpt-4o-mini"
                source = 'openai'


        if source == 'openai':
            try:
                results = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": input
                        }
                    ],

                )
                results = str(results.choices[0].message.content)
                # print(f"openai gave this result: {results}")
                # print(type(results))
            except Exception as e:
                print(f"openai error: {e}")

        return results

    def check_health(self, model, source):
        if source == 'ddgs':
            try:
                results = DDGS().chat("Hi", model=model)
                print("ddgs health check success")
            except Exception as e:
                print(f"ddgs health error: {e}")

                model = "llama-3.3-70b-versatile"
                source = 'groq'
        
        if source == 'groq':
            try:
                results = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ],
                max_tokens=5,
                )
                print("groq health check success")
            except Exception as e:
                print(f"groq health error: {e}")

                model = "gpt-4o-mini"
                source = 'openai'

        if source == 'openai':
            try:
                results = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": "Hi"
                        }
                    ],
                    max_tokens=5,
                )
                print("openai health check success")
            except Exception as e:
                print(f"openai health error: {e}")
                self.health = False

     
        return self.health, model, source
    

