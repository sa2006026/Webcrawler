import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv
import sys

# Set the console encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')



for i in range(1, 2):
    url = f"https://www.southcn.com/node_b5769d65fb?cms_node_post_list_page={i}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_="itm j-link")
    for article in articles:
        date_string = article.find("div", class_="time").text
        datetime_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        print(datetime_obj)
        title = article.find("h3").text.strip()
        link = article.find("a")['href']
        print(title)
        print(link)

