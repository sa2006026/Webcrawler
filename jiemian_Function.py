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
from selenium.common.exceptions import TimeoutException

import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')



def Extract_jiemian_date(from_date, to_date):
    with open('jiemian.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['Title', 'Link', 'Content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            driver_path = r'C:/Users/sa2006026/Downloads/chromedriver.exe'
            driver = webdriver.Chrome(driver_path)
            for i in range(0,3):
                if i == 0:
                    url = 'https://www.jiemian.com/lists/2.html'
                if i == 1:
                    url = 'https://www.jiemian.com/lists/800.html'
                if i == 2:
                    url = 'https://www.jiemian.com/lists/801.html'
                driver.get(url)
                time.sleep(5)
                Last_date = to_date
                while True:
                    if (Last_date >= from_date):
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        article = soup.find_all(class_="card-list")[-1]
                        Last_article = article.find(class_="news-footer__date")
                        Last_date_str = Last_article.text
                        print(Last_date_str)
                        if '昨天' in Last_date_str:
                            Last_date = datetime.today() - timedelta(days=1)
                            try:
                                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '加载更多')]")))
                                button.click()
                                #print(Last_date)
                                time.sleep(5)
                            except TimeoutException:
                                Last_date = from_date - timedelta(days=1)
                                break  # exit the loop if button is not clickable
                        elif '今天' in Last_date_str:
                            Last_date = datetime.today()
                            try:
                                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '加载更多')]")))
                                button.click()
                                #print(Last_date)
                                time.sleep(5)
                            except TimeoutException:
                                Last_date = from_date - timedelta(days=1)
                        else:
                            Last_date = datetime.strptime(Last_date_str, '%m/%d %H:%M')
                            Last_date = Last_date.replace(year=datetime.now().year)
                            try:
                                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '加载更多')]")))
                                button.click()
                                #print(Last_date)
                                time.sleep(5)
                            except TimeoutException:
                                Last_date = from_date - timedelta(days=1)
                                break  # exit the loop if button is not clickable
                    else:
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        articles = soup.find_all('li', {'class': 'card-list'})
                        for article in articles:
                            datetime_str = article.find(class_="news-footer__date").text
                            if '刚刚' in datetime_str:
                                date_1 = datetime.now()
                            elif '分钟前' in datetime_str:
                                date_1 = datetime.now()
                            elif '今天' in datetime_str:
                                date_1 = datetime.now()
                            elif '昨天' in datetime_str:
                                date_1 = datetime.combine(datetime.today() - timedelta(days=1), datetime.max.time())
                            else:
                                date_1 = datetime.strptime(datetime_str, '%m/%d %H:%M')
                                date_1 = date_1.replace(year=datetime.now().year)
                                date_1 = datetime.combine(date_1.date(), datetime.max.time())
                            if date_1 >= from_date:
                                print(date_1)
                                title_element = article.find(class_='card-list__title')
                                title = title_element.text.strip()
                                link_content= article.find('a')['href']
                                link = f"{link_content}"
                                print(link)
                                content_response = requests.get(f"{link}")
                                content_soup = BeautifulSoup(content_response.content, 'html.parser')
                                content_div = content_soup.find('div', class_='article-content')
                                Content_title = content_soup.find('div', class_='article-header').find('h1').text
                                print(Content_title)
                                #print(Content_title)
                                if content_div:
                                    paragraphs = content_div.find_all('p')
                                    content = []
                                    for p in paragraphs:
                                        content.append(p.get_text())
                                else:
                                    content = ["Content not found."]
                                
                                writer.writerow({'Title': title, 'Link': link,
                                                                    'Content': '\n'.join(content)})
                        break
        
#from_date = datetime.today() - timedelta(days=2)  #extract from date

from_date = datetime.strptime('2023-03-10 23:59', '%Y-%m-%d %H:%M')  #extract all   15days only
print(from_date)
to_date = datetime.today() 

Extract_jiemian_date(from_date, to_date)


