# KnowledgeFeed

## Introduction

Welcome to KnowledgeFeed! This is a repository dedicated to curating knowledge on any topic related to your domain. Ever wanted to create your personalised feed of knowledge without wasting countless hours on various social media platforms and research sites? A constant pursuit of knowledge begins here that is intuitive and convinient. This package takes in a topic of your interest and creates a feed of posts with caption-sized facts derived from latest research papers and news articles. Along with that, it also returns relevant images, videos and relevant links to know more. You can choose to skim through, or dive deeper. And none of this without concrete citations.
You can use this output to build your own knowledge bank. You only need to handle personalisation to the topics in the frontend. 
Happy learning!

## How to Contribute

We encourage everyone to contribute to KnowledgeFeed and help build a valuable resource for the community. Here's how you can contribute:

1. Fork the repository to your own GitHub account.
2. Create a new branch for your changes.
3. Make your desired changes, whether it's adding new content, fixing errors, or improving existing content.
4. Commit your changes and push them to your forked repository.
5. Open a pull request to the main repository, explaining the purpose and details of your changes.

Please make sure to follow our contribution guidelines and maintain a respectful and inclusive environment for all contributors.

## How to Use

1. pip install knowledgefeed
2. Get free api key from Groq and put it in your .env file 'GROQ_API_KEY'. You can also put your 'OPENAI_API_KEY'
3. Iterate directly as the function yeilds objects # for item in kf.FeedBuilder().build_feed(user_input, query_type, start): 
4. Take a look at the sample in test.json to know how to utilise this further in your code.
5. You must pass the user_input, query_type and start. Start refers to the slice of query from the search for example 0 -> 0 to max_results, 10 -> 10 to max_results.

## Where to Find Help

If you have any questions or need assistance, you can reach out to the maintainers of this repository or the community of contributors. Feel free to open an issue or join the discussion on the relevant topic.

## License

KnowledgeFeed is released under the [Apache License, Version 2.0]. By contributing to this repository, you agree to make your contributions available under the same license.

We appreciate your interest in contributing to KnowledgeFeed and hope you find it a valuable resource for your learning journey!

