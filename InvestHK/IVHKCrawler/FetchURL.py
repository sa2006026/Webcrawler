import os
from datetime import datetime, timedelta,time
from itertools import count
from urllib.parse import quote, urlencode

import requests
from bs4 import BeautifulSoup

import pandas as pd
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm

from .AnalyzeHTML import *
from .Utils import *


def fetch_url_from_reuters(driver, q, from_date: datetime, to_date: datetime):

    params = {'query': q}

    search_url = 'https://www.reuters.com/site-search/?' + urlencode(params)

    first_page = search_url + '&' + urlencode({'offset': 0})
    num_page_text_elements = fetch_elements_retry_wait(
        driver, first_page, by=By.CSS_SELECTOR, value=".text__text__1FZLe.text__dark-grey__3Ml43.text__medium__1kbOh.text__heading_6__1qUJ5.count")
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
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.CLASS_NAME, value='search-results__item__2oqiX')

        if elements == []:
            break

        def proc_element(e):
            a = e.find_element(by=By.TAG_NAME, value='a')
            try:
                span = a.find_element(by=By.TAG_NAME, value='span')
                title = span.text
            except:
                title = a.text
            timestamp = e.find_element(
                by=By.TAG_NAME, value='time').get_attribute('datetime')

            return {
                'url': a.get_attribute('href'),
                'title': title,
                'datetime': datetime.strptime(timestamp[:10], '%Y-%m-%d'),
            }

        _items = []
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


def fetch_url_from_bloomberg(driver, q, from_date: datetime, to_date: datetime):

    params = {
        'query': q,
        'sort': 'time:desc',
    }

    search_url = 'https://www.bloomberg.com/markets2/api/search?' + \
        urlencode(params)

    result_dfs = []

    for idx in count(1):
        page_url = search_url + '&' + urlencode({'page': idx})
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.TAG_NAME, value='pre')
        page_text = elements[0].text
        d = json.loads(page_text)

        if 'results' not in d.keys() or len(d['results']) == 0:
            break

        _result_df = pd.DataFrame(d['results'])

        def handle_timestamp(x):
            return datetime.strptime(x, '%B %d, %Y')

        _result_df['datetime'] = _result_df['publishedAt'].apply(
            handle_timestamp)
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


def fetch_url_from_cnbc(driver, q, from_date: datetime, to_date: datetime):

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
        page_url = search_url + '&' + urlencode({'endindex': idx * 100})
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.TAG_NAME, value='pre')
        page_text = elements[0].text
        d = json.loads(page_text)

        if 'results' not in d.keys() or len(d['results']) == 0:
            break

        _result_df = pd.DataFrame(d['results'])

        def handle_timestamp(x):
            return datetime.strptime(x[:10], '%Y-%m-%d')

        _result_df['datetime'] = _result_df['datePublished'].apply(
            handle_timestamp)
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


def fetch_url_from_financialtimes(driver, q, from_date: datetime, to_date: datetime):

    params = {
        'q': q,
        'sort': 'date',
        'dateFrom': from_date.strftime('%Y-%m-%d'),
        'dateTo': to_date.strftime('%Y-%m-%d'),
    }

    search_url = 'https://www.ft.com/search?' + urlencode(params)

    page_url = search_url + '&' + urlencode({'page': 1})
    elements = fetch_elements_retry_wait(driver, page_url, by=By.CSS_SELECTOR,
                                         value='.o-teaser-collection__heading.o-teaser-collection__heading--half-width')

    try:
        assert (elements != [])
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
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.CLASS_NAME, value='search-results__list-item')

        if elements == []:
            break

        def proc_element(e):
            elink = e.find_element(
                by=By.CLASS_NAME, value='js-teaser-heading-link')
            etime = e.find_elements(by=By.TAG_NAME, value='time')

            dt = (datetime.strptime(etime[0].text, '%B %d, %Y') if etime != []
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


def fetch_url_from_xinhuanet(driver, q, from_date: datetime, to_date: datetime):

    search_url = 'https://search.news.cn/?lang=en#search/0/' + quote(q)

    page_url = search_url + '/1/'
    elements = fetch_elements_retry_wait(
        driver, page_url, by=By.ID, value='newsCount')
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
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.CLASS_NAME, value='news')

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

        _items = []
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


def fetch_url_from_xinhuanet_chinese(driver, q, from_date: datetime, to_date: datetime):

    search_url = 'http://search.news.cn/#search/0/' + quote(q)

    page_url = search_url + '/1/'
    elements = fetch_elements_retry_wait(
        driver, page_url, by=By.ID, value='newsCount')
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
        elements = fetch_elements_retry_wait(
            driver, page_url, by=By.CLASS_NAME, value='news')

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

        _items = []
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


def fetch_url_from_renminribao(driver, q, from_date: datetime, to_date: datetime):

    def fetchUrl(url):
        '''
        功能：访问 url 的网页，获取网页内容并返回
        参数：目标网页的 url
        返回：目标网页的 html 内容
        '''

        # headers = {
        #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        # }

        driver.get(url)
        return driver.page_source

    def getPageList(year, month, day):
        '''
        功能：获取当天报纸的各版面的链接列表
        参数：年，月，日
        '''
        url = 'http://paper.people.com.cn/rmrb/html/' + year + \
            '-' + month + '/' + day + '/nbs.D110000renmrb_01.htm'
        html = fetchUrl(url)
        bsobj = BeautifulSoup(html, 'html.parser')
        temp = bsobj.find('div', attrs={'id': 'pageList'})
        if temp:
            pageList = temp.ul.find_all(
                'div', attrs={'class': 'right_title-name'})
        else:
            pageList = bsobj.find('div', attrs={
                                  'class': 'swiper-container'}).find_all('div', attrs={'class': 'swiper-slide'})
        linkList = []

        for page in pageList:
            link = page.a["href"]
            url = 'http://paper.people.com.cn/rmrb/html/' + \
                year + '-' + month + '/' + day + '/' + link
            linkList.append(url)

        return linkList

    def getTitleList(year, month, day, pageUrl):
        '''
        功能：获取报纸某一版面的文章链接列表
        参数：年，月，日，该版面的链接
        '''
        html = fetchUrl(pageUrl)
        bsobj = BeautifulSoup(html, 'html.parser')
        temp = bsobj.find('div', attrs={'id': 'titleList'})
        if temp:
            titleList = temp.ul.find_all('li')
        else:
            titleList = bsobj.find(
                'ul', attrs={'class': 'news-list'}).find_all('li')
        linkList = []

        for title in titleList:
            tempList = title.find_all('a')
            for temp in tempList:
                link = temp["href"]
                if 'nw.D110000renmrb' in temp["href"]:
                    r = {
                        'url': 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/' + link,
                        'title': temp.text,
                        'datetime': datetime(int(year), int(month), int(day))
                    }
                    linkList.append(r)

        return linkList

    def gen_dates(b_date, days):
        day = timedelta(days=1)
        for i in range(days):
            yield b_date + day * i

    def get_date_list(beginDate, endDate):
        """
        获取日期列表
        :param start: 开始日期
        :param end: 结束日期
        :return: 开始日期和结束日期之间的日期列表
        """

        data = []
        for d in gen_dates(beginDate, (endDate-beginDate).days):
            data.append(d)
        return data

    def download_rmrb(year, month, day, destdir):
        '''
        功能：爬取《人民日报》网站 某年 某月 某日 的新闻内容，返回格式化记录
        参数：年，月，日，文件保存的根目录
        '''
        pageList = getPageList(year, month, day)
        pbar = tqdm(pageList)
        results = []
        for page in pbar:
            titleList = getTitleList(year, month, day, page)
            results += titleList

        return results

    destdir = "data"

    dates = get_date_list(from_date, to_date)
    # data = rm_existed_dates(destdir, data)
    items = []
    for d in dates:
        year = str(d.year)
        month = str(d.month) if d.month >= 10 else '0' + str(d.month)
        day = str(d.day) if d.day >= 10 else '0' + str(d.day)

        results = download_rmrb(year, month, day, destdir)
        items += results

    result_df = pd.DataFrame(items)
    result_df = result_df.drop_duplicates(['url'])
    result_df = filter_result_df_date(result_df, from_date, to_date)

    ret = result_df.to_dict('records')

    return ret


def fetch_url_from_chinadaily(driver, q, from_date: datetime, to_date: datetime):
    res = []  # url, title, datetime
    # TODO: date time
    i = 0
    datetime_obj = to_date

    while from_date <= datetime_obj:
        i += 1
        url = f"https://www.chinadaily.com.cn/china/governmentandpolicy/page_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('div', class_="mb10 tw3_01_2")
        for article in articles:
            date_string = article.find('b').text
            datetime_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
            date_obj = datetime_obj.date()
            if from_date.date() <= date_obj <= to_date.date():
                title_link = article.find('h4').find('a')
                title = title_link.text.strip()
                link = title_link['href'].lstrip('/')
                res.append(
                    dict(title=title, url=f"http://{link}", datetime=datetime_obj))
            # break # TODO
    return res


def fetch_url_from_GBAChinese(driver, q, from_date: datetime, to_date: datetime):
    res = []  # url, title, datetime
    # TODO: date time
    i = 0
    datetime_obj = to_date

    while from_date <= datetime_obj:
        i += 1
        if i == 1:
            url = "https://www.cnbayarea.org.cn/news/focus/index.html"
        else:
            url = f"https://www.cnbayarea.org.cn/news/focus/index_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for li in soup.select('ul.gl_list1 li'):
            date_string = li.select_one('span.gl_list_date').text
            datetime_obj = datetime.strptime(date_string, '%Y-%m-%d')
            if from_date <= datetime_obj <= to_date:
                #print(datetime_obj)                            #testing
                title = li.select_one('h3.gl_list1_t a').text
                link = li.select_one('h3.gl_list1_t a')['href']
                res.append(dict(title=title, url=f"{link}", datetime=datetime_obj))
            # break # TODO
    return res


def fetch_url_from_GBAEnglish(driver, q, from_date: datetime, to_date: datetime):
    res = []  # url, title, datetime
    # TODO: date time
    i = 0
    datetime_obj = to_date

    while from_date <= datetime_obj:
        i += 1
        if i == 1:
            url = "https://www.cnbayarea.org.cn/english/News/index.html"
        else:
            url = f"https://www.cnbayarea.org.cn/english/News/index_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for li in soup.select('ul.gl_list1 li'):
            date_string = li.select_one('span.gl_list_date').text.strip()
            datetime_obj = datetime.strptime(date_string, '%Y-%m-%d')
            if from_date <= datetime_obj <= to_date:
                #print(datetime_obj)                            #testing
                title = li.select_one('h3.gl_list1_t a').text
                link = li.select_one('h3.gl_list1_t a')['href']
                res.append(dict(title=title, url=f"{link}", datetime=datetime_obj))
            # break # TODO
    return res

def fetch_url_from_SouthCN(driver, q, from_date: datetime, to_date: datetime):
    res = []  # url, title, datetime
    # TODO: date time
    i = 0
    datetime_obj = to_date

    while from_date <= datetime_obj:
        i += 1
        url = f"https://www.southcn.com/node_b5769d65fb?cms_node_post_list_page={i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('div', class_="itm j-link")
        for article in articles:
            date_string = article.find("div", class_="time").text
            datetime_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
            if from_date <= datetime_obj <= to_date:
                title = article.find("h3").text.strip()
                link = article.find("a")['href']
                res.append(dict(title=title, url=f"{link}", datetime=datetime_obj))
            # break # TODO
    return res
