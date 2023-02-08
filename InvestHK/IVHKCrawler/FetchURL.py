from datetime import datetime
from itertools import count
from urllib.parse import quote, urlencode

import pandas as pd
import requests
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm

from .AnalyzeHTML import *
from .Utils import *

def fetch_url_from_reuters(driver, q, from_date:datetime, to_date:datetime):
    
    params = {'query': q}

    search_url = 'https://www.reuters.com/site-search/?' + urlencode(params)
    
    first_page = search_url + '&' + urlencode({'offset': 0})
    num_page_text_elements = fetch_elements_retry_wait(driver, first_page, by=By.CSS_SELECTOR, value=".text__text__1FZLe.text__dark-grey__3Ml43.text__medium__1kbOh.text__heading_6__1qUJ5.count")
    if num_page_text_elements == []:
        logg("Failed fetching total num of pages.")
        return None

    num_total = int(num_page_text_elements[0].text.split(' ')[0])
    num_page = num_total // 20 + 1
    items = []
    logg(f'Sending {num_page} queries to fetch {num_total} news items.')

    for p in tqdm(range(num_page)):
        
        page_url = search_url + '&' + urlencode({'offset': p * 20})
        driver.get(page_url)
        elements = fetch_elements_retry_wait(driver, page_url, by=By.CLASS_NAME, value='search-results__item__2oqiX')
        
        if elements == []:
            break
        
        
        def proc_element(e):
            a = e.find_element(by=By.TAG_NAME, value='a')
            try:
                span = a.find_element(by=By.TAG_NAME, value='span')
                title = span.text
            except:
                title = a.text
            timestamp = e.find_element(by=By.TAG_NAME, value='time').get_attribute('datetime')
            
            return {
                'url': a.get_attribute('href'),
                'title': title,
                'datetime': datetime.strptime(timestamp[:10], '%Y-%m-%d'),
            }
        
        _items  = []
        for e in elements:
            _items.append(proc_element(e))
        
        items += _items
        if any([item['datetime'] < from_date for item in _items]):
            break
    
    result_df = pd.DataFrame(items)
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)
    
    
    ret = result_df.to_dict('records')
        
    return ret

def fetch_url_from_bloomberg(driver, q, from_date:datetime, to_date:datetime):
    
    params = {
        'query': q,
        'sort': 'time:desc',
    }
    
    search_url = 'https://www.bloomberg.com/markets2/api/search?' + urlencode(params)
    
    result_dfs = []
    
    for idx in count(1):
        page_url = search_url + '&' + urlencode({'page': idx})
        elements = fetch_elements_retry_wait(driver, page_url, by=By.TAG_NAME, value='pre')
        page_text = elements[0].text
        d = json.loads(page_text)
        
        if 'results' not in d.keys() or len(d['results']) == 0:
            break
        
        _result_df = pd.DataFrame(d['results'])
        
        def handle_timestamp(x):
            return datetime.strptime(x, '%B %d, %Y')
        
        _result_df['datetime'] = _result_df['publishedAt'].apply(handle_timestamp)
        result_dfs.append(_result_df)
        
        if any(_result_df['datetime'] < from_date):
            break
        
    result_df = pd.concat(result_dfs)
    result_df = result_df[['headline', 'url', 'datetime']]
    result_df.columns = ['title', 'url', 'datetime']
    
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)
    
    ret = result_df.to_dict('records')
        
    return ret

def fetch_url_from_cnbc(driver, q, from_date:datetime, to_date:datetime):
    
    params = {
        'queryly_key': '31a35d40a9a64ab3',
        'query': q,
        'batchsize': 100,
        'timezoneoffset': -480,
        'sort': 'date',
    }
    
    search_url = 'https://api.queryly.com/cnbc/json.aspx?' + urlencode(params)
    
    result_dfs = []
    
    for idx in count(0):
        page_url = search_url + '&' +urlencode({'endindex': idx * 100})
        elements = fetch_elements_retry_wait(driver, page_url, by=By.TAG_NAME, value='pre')
        page_text = elements[0].text
        d = json.loads(page_text)
        
        if 'results' not in d.keys() or len(d['results']) == 0:
            break
        
        _result_df = pd.DataFrame(d['results'])
        
        def handle_timestamp(x):
            return datetime.strptime(x[:10], '%Y-%m-%d')
        
        _result_df['datetime'] = _result_df['datePublished'].apply(handle_timestamp)
        result_dfs.append(_result_df)

        if any(_result_df['datetime'] < from_date):
            break
        
    result_df = pd.concat(result_dfs)
    result_df = result_df[['cn:title', 'url', 'datetime']]
    result_df.columns = ['title', 'url', 'datetime']
    
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)
    
    ret = result_df.to_dict('records')
        
    return ret 



def fetch_url_from_financialtimes(driver, q, from_date:datetime, to_date:datetime):

    params = {
        'q': q,
        'sort': 'date',
        'dateFrom': from_date.strftime('%Y-%m-%d'),
        'dateTo': to_date.strftime('%Y-%m-%d'),
    }

    search_url = 'https://www.ft.com/search?' + urlencode(params)

    page_url = search_url + '&' + urlencode({'page': 1})
    elements = fetch_elements_retry_wait(driver, page_url, by=By.CSS_SELECTOR, value='.o-teaser-collection__heading.o-teaser-collection__heading--half-width')
    
    try:
        assert(elements != [])
        num_total = int(elements[0].text.split(' ')[-1])

    except:
        logg("Failed fetching total num of pages.")
        return None

    num_total = int(elements[0].text.split(' ')[-1])
    num_page = num_total // 25 + 1
    items = []
    logg(f'Sending {num_page} queries to fetch {num_total} news items.')

    for p in range(num_page):
        
        page_url = search_url + '&' + urlencode({'page': p+1})
        elements = fetch_elements_retry_wait(driver, page_url, by=By.CLASS_NAME, value='search-results__list-item')
        
        if elements == []:
            break
        
        
        def proc_element(e):
            elink = e.find_element(by=By.CLASS_NAME, value='js-teaser-heading-link')
            etime = e.find_elements(by=By.TAG_NAME, value='time')
            
            dt =  (datetime.strptime(etime[0].text, '%B %d, %Y') if etime != [] 
                   else _items[-1]['datetime'] if len(_items) > 0 
                   else items[-1]['datetime'] if len(items) > 0 
                   else datetime(1970, 1, 1))
            
            return {
                'url': elink.get_attribute('href'),
                'title': elink.text,
                'datetime': dt,
            }
            
        _items = []
        for e in elements:
            _items.append(proc_element(e))
        
        items += _items
    
    result_df = pd.DataFrame(items)
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)
    
    
    ret = result_df.to_dict('records')
        
    return ret 

def fetch_url_from_xinhuanet(driver, q, from_date:datetime, to_date:datetime):

    search_url = 'https://search.news.cn/?lang=en#search/0/' + quote(q)

    page_url = search_url + '/1/' 
    elements = fetch_elements_retry_wait(driver, page_url, by=By.ID, value='newsCount')
    if elements == []:
        logg("Failed fetching total num of pages.")
        return None

    num_total = int(elements[0].text)
    num_page = num_total // 10 + 1
    items = []
    logg(f'Sending {num_page} queries to fetch {num_total} news items.')

    for p in tqdm(range(num_page)):
        
        page_url = search_url + '/' + str(p+1)
        driver.get(page_url)
        elements = fetch_elements_retry_wait(driver, page_url, by=By.CLASS_NAME, value='news')
        
        if elements == []:
            break
        
        
        def proc_element(e):
            a = e.find_element(by=By.TAG_NAME, value='a')
            span = e.find_element(by=By.TAG_NAME, value='span')
            
            return {
                'url': a.get_attribute('href'),
                'title': a.text,
                'datetime': datetime.strptime(span.text[:10], '%Y-%m-%d'),
            }
        
        _items  = []
        for e in elements:
            _items.append(proc_element(e))
        
        items += _items
        if any([item['datetime'] < from_date for item in _items]):
            break
    
    result_df = pd.DataFrame(items)
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)
    
    
    ret = result_df.to_dict('records')
        
    return ret






