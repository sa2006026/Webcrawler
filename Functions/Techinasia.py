from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time, date
import time
import csv

from_date = datetime.combine(datetime.today(), datetime.min.time()) - timedelta(days=1)
to_date = datetime.combine(datetime.today(), datetime.max.time()) - timedelta(seconds=1)

driver_path = r'D:/User/下載/chromedriver.exe'
driver = webdriver.Chrome(driver_path)
url = 'https://www.techinasia.com/category/news'
driver.get(url)
time.sleep(5)
Last_date = to_date
while True:
    if Last_date >= from_date:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        Last_article = soup.find_all('div', {'class': 'web-document'})[-1]
        Last_date_str = Last_article.find(class_="split-center").find_next('div').text
        if 'hours ago' in Last_date_str:
            now = datetime.now()
            hours = int(Last_date_str.split()[0])
            Last_date = (now - timedelta(hours=hours))
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(4)
        else:
            Last_date = datetime.strptime(Last_date_str, '%b %d %Y')
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(4)
    else:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', {'class': 'web-document'})
        for article in articles:
            datetime_str = article.find(class_="split-center").find_next('div').text
            if 'hours ago' in datetime_str:
                now = datetime.now()
                hours = int(datetime_str.split()[0])
                date_1 = (now - timedelta(hours=hours))
            elif 'a day ago' in datetime_str:
                date_1 = (datetime.today() - timedelta(days=1))
            elif 'minutes ago' in datetime_str:
                date_1 = datetime.now()
            elif 'minute ago' in datetime_str:
                date_1 = datetime.now()
            elif 'hour ago' in datetime_str:
                date_1 = datetime.now()
            else:
                date_1 = datetime.strptime(datetime_str, '%b %d %Y')
            if date_1 >= from_date:
                title_element = article.find(class_='title')
                title = title_element.text.strip()
                link_content= article.find('a')['href']
                link = f"https://www.yicaiglobal.com{link_content}"
                #print(title, link)
                content_response = requests.get(f"{link}")
                content_soup = BeautifulSoup(content_response.content, 'html.parser')
                content_div = content_soup.find(class_="display_flex flex-direction_column detail-content")
                Content_title = content_soup.find(class_="detail-title").text
                #print(Content_title)
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = []
                    for p in paragraphs:
                        content.append(p.get_text())
                    else:
                        content = ["No Text Content"]
                else:
                    content = ["Content not found."]

                writer.writerow({'Title': title, 'Link': link,
                                    'Content': '\n'.join(content)})

        break


#format_string = '%I:%M %p at %b %d, %Y'