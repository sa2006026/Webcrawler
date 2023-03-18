import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv


def Extract_AVCJ_date(from_date, to_date):
    with open('AVCJ.csv', mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Link', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        i = 0
        datetime_obj = to_date

        while from_date <= datetime_obj:
            i += 1
            url = f"https://www.avcj.com/type/news/page/{i}"
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
                    content_response = requests.get(f"{link}")
                    content_soup = BeautifulSoup(
                        content_response.content, 'html.parser')
                    content_div = content_soup.find('p', class_="article-summary")
                    Content_title = content_soup.find(class_="article-title").text

                    if content_div:
                        paragraphs = content_div.find_all('b')
                        content = []
                        for b in paragraphs:
                            content.append(b.get_text())
                    else:
                        content = ["Content not found."]

                    # Write row to CSV
                    writer.writerow({'Title': title, 'Link': link,
                                     'Content': '\n'.join(content)})


def Extract_AVCJ_all():
    with open('AVCJ.csv', mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Link', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, 4):
            url = f"https://www.avcj.com/type/news/page/{i}"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', class_="col span_4_of_4")
            # Extract title, content and link
            for article in articles:
                date = article.find('time')['datetime']
                datetime_obj = datetime.strptime(date, '%Y-%m-%d')
                print(datetime_obj)  # checking datetime of news extracted
                link_content= article.find('a')['href']
                title = article.find('h5', class_='listings-article-title').text.strip()
                link = f"https://www.avcj.com{link_content}"
                content_response = requests.get(f"{link}")
                content_soup = BeautifulSoup(
                    content_response.content, 'html.parser')
                content_div = content_soup.find('p', class_="article-summary")
                Content_title = content_soup.find(class_="article-title").text

                if content_div:
                    paragraphs = content_div.find_all('b')
                    content = []
                    for b in paragraphs:
                        content.append(b.get_text())
                else:
                    content = ["Content not found."]

                # Write row to CSV
                writer.writerow({'Title': title, 'Link': link,
                                    'Content': '\n'.join(content)})


# Example

"""today = datetime.today()
from_date = datetime.combine(
    today - timedelta(days=2), time.min)  # change days
to_date = datetime.combine(today, time.max) - \
    timedelta(seconds=1)  # today datetime

Extract_AVCJ_date(from_date, to_date)"""

Extract_AVCJ_all()
