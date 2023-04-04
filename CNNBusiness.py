import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv
import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def Extract_GBAChinese_all():
    with open('CNNBusiness.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['Title', 'Link', 'Content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            url = f"https://edition.cnn.com/business"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all(class_="container__link container_lead-plus-headlines-with-images__link")
            # Extract title, content and link
            links = soup.find_all('a', class_='container__link')
            unique_links = set()
            unique_articles = set()

            for link_1 in links:
                article_1 = link_1.find(class_='container__headline')
                if article_1 is not None:
                    article_1 = link_1.find('div', class_='container__headline').text.strip()
                    if article_1 not in unique_articles:
                            unique_articles.add(article_1)
                            title = article_1
                            link_1 = link_1.get('href')
                            if link_1.startswith('https://www.cnn.com/interactive'):
                                link_1 = link_1.replace('https://www.cnn.com', '')
                            link = f"https://www.cnn.com{link_1}"
                            content_response = requests.get(f"{link}")
                            content_soup = BeautifulSoup(content_response.content, 'html.parser')
                            content_div = content_soup.find(class_="article__content")
                            content_title = content_soup.find(class_="headline__text inline-placeholder")
                            if content_title is not None:
                                content_title = content_title.text.strip()
                            if content_div:
                                paragraphs = content_div.find_all('p')
                                content = []
                                if paragraphs:
                                    for p in paragraphs:
                                        content.append(p.text.strip())
                                else:
                                    content = ["No Text Content"]
                            else:
                                content = ["No Text Content"]

                            writer.writerow({'Title': title, 'Link': link,
                                    'Content': '\n'.join(content)})

Extract_GBAChinese_all()