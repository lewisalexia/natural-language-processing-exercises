#standard imports
import pandas as pd

#my module
import wrangle as wr

#scrape/html imports
import requests
from requests import get
from bs4 import BeautifulSoup
from pprint import pprint

#sleep timer
import time

#import regex
import re

#import file
import os
import json

#prepare imports
import unicodedata
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords

# -----------------------------------------------------------------ACQUIRE-----------------------------------------------------------------

def get_blog_articles():
    '''
    this function checks for a json file of scraped data. If no file exists, it scrapes and runs
    the function again then saves to a json in local directoty. returns df of items.
    '''
    file = "blog_posts.json"
    
    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
        
    headers = {'User-Agent': 'Codeup Data Science'}
    article_info = []

    for link in links_list:
        response = get(link, headers=headers)
        more_links = soup.find_all('a', class_='more-link')
        links_list = [link['href'] for link in more_links]

        soup = BeautifulSoup(response.content, 'html.parser')

        info_dict = {"title":soup.find("h1").text,
                    "link": link,
                    "date_published":soup.find('span', class_="published").text,
                    "content": soup.find('div', class_="entry-content").text.replace('\n',' ')}
        article_info.append(info_dict)
    
    with open(file, "w") as f:
        json.dump(article_info, f)
        
    return article_info

def get_news_articles():
    '''
    this function gets the top 25 news articles titles, content, and category from inshorts.com
    category is only business, sports, technology, and entertainment. returns results list.
    ---
    format: results = function() 
        ***convert to df with this pd option: pd.set_option("display.max_colwidth", None)***
    '''
    file = 'news_articles.json'
    
    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
            print('file found and loaded')
    print(f'file not found. scraping and writing to json file')
    
    #create a dictionary and a list to store variables
    soup_dict_ = {} #stores soup calls for each of the endpoints in url_list
    response_list = [] #stores the responses to iterate
    title_list = []
    content_list = []
    category_list = []

    #make url_list to cycle through the sites I want because it was too complicated the other way
    url_list = ['/business', '/sports', '/technology', '/entertainment']

    #access the website - not blocked, accepts python requests
    url = 'https://inshorts.com/en/read'
    response = get(url)

    #cycle through list with timer to allow for load time printing response to ensure I have access
    for endpoint in url_list:
        response = get(url)
        print(f'{url}{endpoint}')
        time.sleep(5)
        print(response)
        response_list.append(response)
        print(f'access granted')

        #iterate through the response_list and create a soup variable for each response
        for endpoint, response in zip(url_list, response_list):
            soup = BeautifulSoup(response.content, 'html.parser')
            soup_dict_[endpoint.replace('/','')] = soup

            #create variables
            titles = soup.find_all(itemprop='headline')
            contents = soup.find_all(itemprop='articleBody')

            #establishing range for loop
            num_titles = len(soup.find_all(itemprop='headline'))
            num_content = len(soup.find_all(itemprop='articleBody'))
            num_category = len(soup.find_all(itemprop='articleBody'))

        #using np.arange to iterate through 
        for i in np.arange(num_titles):
            title_list.append(titles[i].text)
        for i in np.arange(num_content):
            content_list.append(contents[i].text)
        for i in np.arange(num_category):
            category_list.append(endpoint.replace('/',''))

        #combine lists to one dictionary following assigned format
        results = {'title':title_list,
                   'content':content_list,
                   'category':category_list}

    with open(file, 'w') as f:
        json.dump(results, f)
        
    return results

# -----------------------------------------------------------------PREPARE-----------------------------------------------------------------

