from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta, time
import sys

sys.stdout.reconfigure(encoding='utf-8')
today = datetime.today()
from_date = datetime.combine(
    today - timedelta(days=1), time.min)  # change days
to_date = datetime.combine(today, time.max) - \
    timedelta(seconds=1)  # today datetime

url = f"https://www.avcj.com/type/news/page/1"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all('article', class_="col span_4_of_4")
# Extract title, content and link
for article in articles:
    date = article.find('time')['datetime']
    datetime_obj = datetime.strptime(date, '%Y-%m-%d')
    if from_date <= datetime_obj <= to_date:
        print(datetime_obj)  # checking datetime of news extracted
        link_content= article.find('a')['href']
        title = article.find('h5', class_='listings-article-title').text.strip()
        link = f"https://www.avcj.com{link_content}"





