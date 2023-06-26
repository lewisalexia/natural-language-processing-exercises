#standard imports
import pandas as pd

#my module
import env

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

print(f'imports loaded successfully, awaiting commands...')

def get_connection(db):
    '''
    establishes connection to mysql server using env.py credentials
    ---
    Format: url = function()
    '''
    #returns url to access mysql server
    return f'mysql+pymysql://{env.user}:{env.password}@{env.host}/{db}'

def check_file_exists(fn, query, url):
    '''
    check if file exists in my local directory, if not, pull from sql db
    return dataframe and save to a csv in the local directory
    '''
    #if/else file exists in local directory
    if os.path.isfile(fn):
        print('csv file found and loaded')
        return pd.read_csv(fn, index_col=0)
    else: 
        print('creating df and exporting csv')
        df = pd.read_sql(query, url)
        df.to_csv(fn)
        return df 

def get_sql(filename, db, query='show tables;'):
    """
    Retrieves logs data from the specified database table and saves it as a CSV file.
    """
    #use the current working directory as the directory path
    directory = os.getcwd() + "/"  

    if os.path.exists(directory + filename):
        df = pd.read_csv(directory + filename, index_col=0)
        return df
    else:
        url = env.get_db_url({db})
        conn = create_engine(url).connect()
        df = pd.read_sql(query, conn)
        df.to_csv(directory + filename, index_col=0)
        return df

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

#create lowercase function
def lower_everything(string):
    return string.str.lower()

def normalize_everything(string):
    string = unicodedata.normalize('NFKD', string).encode('ascii','ignore').decode('utf-8')
    return string

#create removal of specials function
def specials_removed(string):
    string = re.sub(r'[^a-z0-9\'\s]', '', string)
    return string

def basic_clean(string):
    string = string.lower()
    string = unicodedata.normalize('NFKD', string).encode('ascii','ignore').decode('utf-8')
    string = re.sub(r'[^a-z0-9\'\s]', '', string)

    return string

def token_it_up(string):
    tokenize = nltk.tokenize.ToktokTokenizer()
    string = tokenize.tokenize(string, return_str=True)
    return string

def stemmer(string):
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in string.split()]
    string = ' '.join(stems)
    return string

def lemmad(string):
    wnl = nltk.stem.WordNetLemmatizer()
    string = [wnl.lemmatize(word) for word in string.split()]
    string = ' '.join(string)
    return string

def remove_stopwords(string, extra_words=[], exclude_words=[]):
    sls = stopwords.words('english')
    
    sls = set(sls) - set(exclude_words)
    sls = sls.union(set(extra_words))
    
    words = string.split()
    filtered = [word for word in words if word not in sls]
    string = ' '.join(filtered)
    return string

def clean_df(df, exclude_words=[], extra_words=[]):
    '''
    send in df with columns: title and original,
    returns df with original, clean, stemmed, and lemmatized data
    '''
    df['clean'] = df.original.apply(basic_clean).apply(token_it_up).apply(remove_stopwords)
    df['stem'] = df.clean.apply(stemmer)
    df['lemma'] = df.clean.apply(lemmad)
    
    return df


def clean(text):
    '''
    A simple function to cleanup text data.
    
    Args:
        text (str): The text to be cleaned.
        
    Returns:
        list: A list of lemmatized words after cleaning.
    '''
    #assigning additional stopwords
    ADDITIONAL_STOPWORDS = ['r', 'u', '2', '4', 'ltgt']
    
    # basic_clean() function from last lesson:
    # Normalize text by removing diacritics, encoding to ASCII, decoding to UTF-8, and converting to lowercase
    text = (unicodedata.normalize('NFKD', text)
             .encode('ascii', 'ignore')
             .decode('utf-8', 'ignore') #most frequently used for base text creation - works great with SQL
             .lower())
    
    # Remove punctuation, split text into words
    words = re.sub(r'[^\w\s]', '', text).split()
    
    
    # lemmatize() function from last lesson:
    # Initialize WordNet lemmatizer
    wnl = nltk.stem.WordNetLemmatizer()
    
    # Combine standard English stopwords with additional stopwords
    stopwords = nltk.corpus.stopwords.words('english') + ADDITIONAL_STOPWORDS
    
    # Lemmatize words and remove stopwords
    cleaned_words = [wnl.lemmatize(word) for word in words if word not in stopwords]
    
    return cleaned_words