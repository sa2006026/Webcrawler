import json
import re
from importlib.resources import contents

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

from .Utils import *

def return_empty_when_error(func):
    
    def wrapper(*args, **kwargs):
        
        try:
            ret = func(*args, *kwargs)
        except:
            ret = ([], [])
            logg("Error occurred when analyze HTML.")
            
        return ret
    
    return wrapper

@return_empty_when_error
def analyze_common_schema(soup:BeautifulSoup):
    titles, contents = [], []
    for json_text in soup.find_all('script', type='application/ld+json'):
        try:
            d = json.loads(json_text.text.strip())
            if type(d) != type({}):
                continue
        except:
            continue
        
        if 'articleBody' in d.keys() and 'headline' in d.keys():
            titles.append(d['headline'])
            contents.append(d['articleBody'])
    return titles, contents

@return_empty_when_error
def analyze_washingtonpost(soup:BeautifulSoup):
    headline_element = soup.find('span', **{'data-qa': 'headline-text'})
    titles, contents = [], []
    if headline_element is not None and hasattr(headline_element, 'text'):
        titles = [headline_element.text]
        jtext = soup.find_all('script', id='__NEXT_DATA__')[0].text.strip()
        d = json.loads(jtext)
        content_elements = d['props']['pageProps']['globalContent']['content_elements']
        content = ''
        for e in content_elements:
            if e['type'] == 'text':
                content += e['content']
        contents = [content]
    return titles, contents


@return_empty_when_error
def analyze_bloomberg_article(soup:BeautifulSoup):
    d = json.loads(soup.find(**{'data-component-props':"ArticleBody"}).text)
    body_soup = BeautifulSoup(d['story']['body'], features="lxml")
    elements = body_soup.find_all('p')
    contents = [''.join([e.text for e in elements])]
    titles = [d['story']['headline']]
    return titles, contents

@return_empty_when_error
def analyze_bloomberg_video(soup:BeautifulSoup):
    t = soup.find_all(**{'class': 'google-structured-data', 'type':"application/ld+json"})[0].text.strip()
    d = json.loads(t)
    tc = '' if d['video']['transcript'] is None else d['video']['transcript']
    contents = [d['description'] + tc]
    titles = [d['headline']]
    return titles, contents


@return_empty_when_error
def analyze_cnbc_article(soup:BeautifulSoup):
    content = soup.find(**{'data-module': "ArticleBody"}).text.strip()
    title = soup.find('h1', **{'class': "ArticleHeader-headline"}).text.strip()
    contents = [content]
    titles = [title]

    return titles, contents

@return_empty_when_error
def analyze_cnbc_id(soup:BeautifulSoup):
    content = soup.find(**{'itemprop': "articleBody"}).text.strip()
    title = soup.find('h1', **{'class': "title"}).text.strip()
    contents = [content]
    titles = [title]

    return titles, contents


@return_empty_when_error
def analyze_cnbc_video(soup:BeautifulSoup):
    content = soup.find(**{'class': re.compile(f'^.*{"clipPlayerIntroSummary"}.*$')}).text.strip()
    title = soup.find('h1', **{'class': re.compile(f'^.*{"clipPlayerIntroTitle"}.*$')}).text.strip()
    contents = [content]
    titles = [title]
    return titles, contents

@return_empty_when_error
def analyze_financialtimes_video(soup:BeautifulSoup):
    titles = [soup.find('title').text]
    transcript_lines = soup.find('div', **{'class': 'video__transcript__text'}).find_all('p')[1:]
    content = ' '.join([element.text for element in transcript_lines])
    contents = [content]

    return titles, contents

@return_empty_when_error
def analyze_financialtimes_content(soup:BeautifulSoup):
    return analyze_common_schema(soup)

@return_empty_when_error
def analyze_financialtimes_livepost(soup:BeautifulSoup):
    titles = [element.text for element in soup.find_all(**{'class': 'x-live-blog-post__title'})]
    contents = [element.text for element in soup.find_all(**{'class': 'x-live-blog-post__body n-content-body article--body'})]
    if not len(titles) == len(contents):
        logg("Titles & Contents length dont match.")
        return [], []

    return titles, contents

@return_empty_when_error
def analyze_xinhuanet_article(soup:BeautifulSoup):

    # Old Format
    title = soup.find('h1', **{'class': 'Btitle'})
    if title is not None:
        titles = [title.text.strip()]
        contents = [soup.find('div', **{'class': 'content'}).text.strip()]

    # New format since 2021
    else:
        titles = [soup.find('title').text.strip()]
        contents = [soup.find(**{'id': 'detailContent'}).text.strip()]

    return titles, contents

@return_empty_when_error
def analyze_xinhuanet_article_chinese(soup:BeautifulSoup):

    titles = [soup.find('span', **{'class': 'title'}).text.strip()]
    contents = [''.join([p.text.strip() for p in soup.find('div', id='detail').find_all('p')])]

    return titles, contents

@return_empty_when_error
def analyze_reuters_article(soup:BeautifulSoup):
    
    titles = [soup.find('h1', {'data-testid': 'Heading'}).text]
    paragraphs = soup.find_all('p', {'class': "text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__large__nEccO body__full_width__ekUdw body__large_body__FV5_X article-body__element__2p5pI"})
    contents = ['\n'.join([p.text for p in paragraphs])]
    
    return titles, contents

@return_empty_when_error
def analyze_xinhuanet_article_chinese(soup:BeautifulSoup):

    titles = [soup.find('span', **{'class': 'title'}).text.strip()]
    contents = [''.join([p.text.strip() for p in soup.find('div', id='detail').find_all('p')])]

    return titles, contents

@return_empty_when_error
def analyze_reuters_article(soup:BeautifulSoup):
    
    titles = [soup.find('h1', {'data-testid': 'Heading'}).text]
    paragraphs = soup.find_all('p', {'class': "text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__large__nEccO body__full_width__ekUdw body__large_body__FV5_X article-body__element__2p5pI"})
    contents = ['\n'.join([p.text for p in paragraphs])]
    
    return titles, contents

@return_empty_when_error
def analyze_renminribao_article(soup:BeautifulSoup):
    
    titles = [soup.find('title').text]
    contents = ['\n'.join([p.text for p in soup.find(**{'id': 'articleContent'}).find_all('p')])]
    
    return titles, contents


@return_empty_when_error
def analyze_chinadaily_article(soup:BeautifulSoup):
    
    titles = [soup.find('h1').getText()] # TODO
    
    content_div = soup.find('div', id='Content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = []
        for p in paragraphs:
            content.append(p.get_text())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)

    
    return titles, contents

@return_empty_when_error
def analyze_GBAChinese_article(soup:BeautifulSoup):
    
    titles = [soup.find('h1', class_="article_t").text] # TODO
    
    content_div = soup.find('div', class_="article_con")
    if content_div:
        paragraphs = content_div.find_all(
            'p', {'style': 'text-align: justify;'})
        content = []
        for p in paragraphs:
            if p.text.strip():  
                content.append(p.text.strip())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)

    
    return titles, contents

@return_empty_when_error
def analyze_GBAEnglish_article(soup:BeautifulSoup):
    
    titles = [soup.find('h1', class_="article_t").text] # TODO
    
    content_div = soup.find('div', class_="article_con")
    if content_div:
        paragraphs = content_div.find_all(
            'p', {'style': 'text-align: left;'})
        content = []
        for p in paragraphs:
            if p.text.strip():  
                content.append(p.text.strip())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)
    
    return titles, contents

@return_empty_when_error
def analyze_SouthCN_article(soup:BeautifulSoup):
    
    titles = [soup.find(id_="article_title")] # TODO
    
    content_div = soup.find('div', class_="m-article")
    if content_div:
        paragraphs = content_div.find_all(
                            'p', {'style': 'text-align: justify;'})
        content = []
        for p in paragraphs:
            if p.text.strip():  
                content.append(p.text.strip())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)
    
    return titles, contents

@return_empty_when_error
def analyze_AVCJ_article(soup:BeautifulSoup):
    
    titles = [soup.find(class_="article-title").text] # TODO
    
    content_div = soup.find('b', class_="article-summary")
    if content_div:
        paragraphs = content_div.find_all('b')
        content = []
        for b in paragraphs:
            content.append(b.get_text())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)
    
    return titles, contents

@return_empty_when_error
def analyze_YiCai_article(soup:BeautifulSoup):
    
    titles = [soup.find(class_="detail-title").text] # TODO
    
    content_div = soup.find(class_="display_flex flex-direction_column detail-content")
    if content_div:
        paragraphs = content_div.find_all('p')
        content = []
        for p in paragraphs:
            content.append(p.get_text())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)
    
    return titles, contents

@return_empty_when_error
def analyze_jiemian_article(soup:BeautifulSoup):
    
    titles = [soup.find('div', class_='article-header').find('h1').text] # TODO
    
    content_div = soup.find('div', class_='article-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = []
        for p in paragraphs:
            content.append(p.get_text())
    else:
        content = ["Content not found."]
    contents = "\n".join(content)
    
    return titles, contents