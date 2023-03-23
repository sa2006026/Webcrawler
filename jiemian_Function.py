from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time,date
import time
import csv

def Extract_YiCai_date(from_date, to_date):
    with open('YiCai.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['Title', 'Link', 'Content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            driver_path = r'D:/User/下載/chromedriver.exe'
            driver = webdriver.Chrome(driver_path)
            for i in range(0,1):
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
                    if Last_date >= from_date:
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        Last_article = soup.find_all('div', {'class': 'web-document'})[-1]
                        Last_date_str = Last_article.find(class_="split-center").find_next('div').text
                        if 'hours ago' in Last_date_str:
                            now = datetime.now()
                            hours = int(Last_date_str.split()[0])
                            Last_date = (now - timedelta(hours=hours))
                            load_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".channel-load-more")))
                            load_more_button.click()
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
                                    content = ["Content not found."]

                                writer.writerow({'Title': title, 'Link': link,
                                                    'Content': '\n'.join(content)})

                        break

from_date = datetime.today() - timedelta(days=1)  #extract from date

#from_date = datetime.strptime('2020-01-01', '%Y-%m-%d')  #extract all

to_date = datetime.today()                                          #must open
Extract_YiCai_date(from_date, to_date)                          #must open


