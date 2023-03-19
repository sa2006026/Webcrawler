from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv


# Set up Selenium web driver (you need to download the appropriate driver for your browser)
driver = webdriver.Chrome('C:/Users/sa2006026/Downloads/chromedriver')

# Load initial page
driver.get('https://en.caixin.com/')

def Extract_AVCJ_date(from_date, to_date):
    with open('AVCJ.csv', mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Link', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        i = 0
        datetime_obj = to_date
        url = "https://en.caixin.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('dl')

        # Find all datetime_obj in articles
        for article in articles:
            date_elem = article.find('span')
            print(date_elem)
            if date_elem is not None:
                date = date_elem.text.strip()
                datetime_obj = datetime.strptime(date.replace('�~', '-').replace('��', ''), '%Y-%m-%d')

                

        # Check if the date of the last article is greater than or equal to the from_date
        last_article_date_elem = articles[-2].find('span')
        last_article_date = datetime.strptime(last_article_date_elem.text.strip(), '%Y年%m月%d日')
        while last_article_date >= from_date:
            # Click the button to load more content
            load_more_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "加载更多文章")]')))
            driver.execute_script("arguments[0].click();", load_more_button)

            # Extract the articles again after clicking the button
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.find_all('dl')

            # Find all datetime_obj in articles
            for article in articles:
                date_elem = article.find('span')
                if date_elem is not None:
                    date = date_elem.text.strip()
                    datetime_obj = datetime.strptime(date, '%Y年%m月%d日')

            # Check if the date of the last article is greater than or equal to the from_date
            last_article_date_elem = articles[-2].find('span')
            last_article_date = datetime.strptime(last_article_date_elem.text.strip(), '%Y年%m月%d日')

        # Loop through all articles and collect the data
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
                    content_response = requests.get(f"{link}")
                    content_soup = BeautifulSoup(
                        content_response.content, 'html.parser')
                    content_div = content_soup.find('div', id_="Main_Content_Val")
                    Content_title = content_soup.find('h1').text.strip()
                    if content_div:
                        paragraphs = content_div.find_all('p')
                        content = []
                        for p in paragraphs:
                            content.append(p.get_text())
                    else:
                        content = ["Content not found."]

                    # Write row to CSV
                    writer.writerow({'Title': title, 'Link': link,
                                    'Content': '\n'.join(content)})

# Check if the date of the last article is greater than or equal to the from_date
        

    # Quit the Selenium web driver
    driver.quit()


today = datetime.today()
from_date = datetime.combine(
    today - timedelta(days=60), time.min)  # change days
to_date = datetime.combine(today, time.max) - \
    timedelta(seconds=1)  # today datetime

Extract_AVCJ_date(from_date, to_date)

# close the webdriver
