import copy
import sys
import json
import re
import requests
import urllib, urllib.request
import xml.etree.ElementTree as ET
from duckduckgo_search import DDGS
from docling.document_converter import DocumentConverter
from openai import OpenAI
import os
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




# for now, user only gives text input.
# so the feed needs to be constructed with only topic names.
# the topic names lead to either research papers, news articles, blogs, images, or videos.
# the decision to categorize, shall be taken by an llm based on a predetermined logic.
# according to the category, DDGS will fetch the relevant sources.
# the output of this part should be a text file.
# text can be empty for images and videos, that will be fed in the resources field.



class Fetcher:
    def __init__(self):
        pass

    def categoriser(self, query, query_type='business',start=0):
        query = query.strip().split(' ').join('+')
        query_type = query_type.lower()
        allContent = []
        converter = DocumentConverter()
        
        if query_type == 'academic':
            
            url = f'http://export.arxiv.org/api/query?search_query={query}&start={start}&max_results=10'
            try:
                xml_data = urllib.request.urlopen(url).read().decode('utf-8')
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


            for source in pdf_sources:
                news_sources = DDGS().news(query, max_results=2)
                img_sources = DDGS().images(query, max_results=2)
                video_sources = DDGS().videos(query, max_results=2)
                md_str = converter.convert(source)
                md_str = md_str.document.export_to_markdown()
                
                # add more to return resources if found
                resources = {
                    'images' : img_sources, # list of objects
                    'videos' : video_sources, # list of objects
                    'newsArticles': news_sources, # list of objects
                }

                allContent.append({'pdflink': source, 'md_str': md_str, 'resources': resources})

        else:
            news_sources = DDGS().news(query, max_results=10)
            img_sources = DDGS().images(query, max_results=2)
            video_sources = DDGS().videos(query, max_results=2)
            resources = {
                'images' : img_sources, # list of objects
                'videos' : video_sources, # list of objects
            }
            for news in news_sources:
                # replace this with processing of news articles
                url = news['url']
                md_str = converter.convert(url)
                md_str = md_str.document.export_to_markdown()
                allContent.append({'abslink': news['url'], 'md_str': md_str, 'resources': resources})

        return allContent
    

class FeedBuilder:
    
    def __init__(self):
        pass

    def build_feed(self, user_input, query_type):
        allContent = Fetcher().categoriser(user_input, query_type)
        feed = []
        for content in allContent:
            abslink = content.get('abslink', None)
            pdflink = content.get('pdflink', None)
            md_str = content.get('md_str', None)
            resources = content.get('resources', None)
            model = 'llama-3.3-70b'
            source = 'DDGS'
            temp = 0.7
            personality = 'friendly'
            ob = ObjectBuilder()
            feed.append(ob.build_object(abslink, pdflink, md_str, model, source, temp, personality, resources))
            
        return feed


class Feed:
    id = -1

    def idgenerator(self):
        self.id += 1
        return self.id


    def __init__(self, abslink, pdflink, md_str):
        self.abslink = abslink
        self.pdflink = pdflink
        self.md_str = md_str
        self.id = self.idgenerator()
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

    id = -1

    def idgenerator(self):
        self.id += 1
        return self.id

    def __init__(self, text, chatContext, resources):
        self.text = text
        self.chatContext = chatContext
        self.resources = resources
        self.id = self.idgenerator()
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
        pass

    def build_posts(self, md_str, resources):
        self.md_str = md_str
        self.recources = resources
        posts = Posts()
        try:
            results = DDGS().chat(f"Chunk this text into meaningful parts and only return a list object: {md_str}", model='llama-3.3-70b')
        except Exception as e:
            sys.stdout.write(f"Error: {e}\nUsing OpenAI instead\n")
            openaiResponse = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "assistant", "content": "Chunk this text into meaningful parts and only return a list object:"},
                    {"role": "user", "content": md_str},
                ]
            )
            results = openaiResponse.choices[0].message.content
        try:
            sentences = json.loads(results)
            for i, sentence in enumerate(sentences):
                post = Post(sentence, md_str, resources)
                posts.add_post(post.get_post())

        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON: {e}")

        # print(posts.get_posts())
        return posts

    def build_object(self, abslink, pdflink, md_str, model, source, temp, personality, resources):
        feed_object = Feed(abslink, pdflink, md_str)
        agent = Agent(model, source, temp, personality)
        feed_object.add_agent(agent.get_agent())
        
        posts = self.build_posts(md_str, resources)
        
        feed_object.add_posts(posts.get_posts())
        sys.stdout.write('Feed built successfully!\n')
        return feed_object.get_feed()


class HeathChecker():
    def __init__(self, model, source):
        self.source = source
        self.model = model
        self.source.lower()
        self.health = True
        if source == 'ddgs':
            try:
                results = DDGS().chat("Hi", model=model, max_tokens=1)
            except Exception as e:
                self.health = False
        
        if source == 'groq':
            try:
                results = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "You are a smart, sophisticated human with great attention to detial. Give me a short introduction to agentic ai platforms."
                    }
                ],
                max_tokens=1,
                )
            except Exception as e:
                self.health = False

        


     
        return self.health