from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta, time
import sys

sys.stdout.reconfigure(encoding='utf-8')

today = datetime.today()
from_date = datetime.combine(
    today - timedelta(days=5), time.min)  # change days
to_date = datetime.combine(today, time.max) - \
    timedelta(seconds=1)  # today datetime

i = 0
datetime_obj = to_date



url = "https://en.caixin.com/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all('dl')
# Extract title, content and link
for article in articles:
    date_elem = article.find('span')
    if date_elem is not None:
        date = date_elem.text.strip()
        datetime_obj = datetime.strptime(date, '%Y年%m月%d日')
        if from_date <= datetime_obj <= to_date:
            print(datetime_obj)  # checking datetime of news extracted
            link_content= article.find('a')['href']
            title = article.find('img')['alt']
            link = f"{link_content}"
            print(title)
            print(link)




