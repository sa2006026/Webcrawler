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

import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

driver_path = r'D:/User/下載/chromedriver.exe'
driver = webdriver.Chrome(driver_path)
for i in range(0,1):
    if i == 0:
        url = 'https://www.jiemian.com/lists/2.html'
driver.get(url)
titles = driver.find_elements(By.CLASS_NAME,"card-list__title")
for title in titles:
    print(title.text)

driver.quit()


"""from bs4 import BeautifulSoup
import requests

url = 'https://www.jiemian.com/lists/2.html'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

news_list = soup.find_all('li', class_='card-list')

for news in news_list:
    title = news.find('h3', class_='card-list__title').text.strip()
    date = news.find('span', class_='news-footer__date').text.strip()

    # Encode using latin1, decode using utf-8
    title = title.encode('latin1').decode('utf-8')
    print('Title:', title)
    print('Date:', date)
"""