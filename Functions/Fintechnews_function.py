import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv
import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def Extract_Fintechnews_all():
    with open('Fintechnews.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['Title', 'Link', 'Content']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            url = f"https://fintechnews.hk/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all(class_="item")
            for article in articles:
                title_1 = article.find(class_='entry-title')
                if title_1 is not None:
                    title = title_1.text
                    link = article.find('a')['href']
                    content_response = requests.get(f"{link}")
                    content_soup = BeautifulSoup(content_response.content, 'html.parser')
                    content_div = content_soup.find(class_='article-content')
                    Content_title = content_soup.find(class_='article-header')
                    if Content_title is not None:
                        Content_title = Content_title.find('h1').text.strip()
                    if content_div:
                        paragraphs = content_div.find_all('p')
                        content = []
                        if paragraphs:
                            for p in paragraphs:
                                content.append(p.text.strip())
                        else:
                            content = ["No Text Content"]
                    else:
                        content = ["Content not found."]
                    writer.writerow({'Title': title, 'Link': link,
                                                'Content': '\n'.join(content)})
                    
Extract_Fintechnews_all()
