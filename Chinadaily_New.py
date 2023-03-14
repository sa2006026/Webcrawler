import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv

to_date = datetime.today()
from_date = datetime.today() - timedelta(days=2)

with open('chinadaily2.csv', mode='w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['Title', 'Link', 'Content']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, 3):
        url = f"https://www.chinadaily.com.cn/china/governmentandpolicy/page_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('div', class_="mb10 tw3_01_2")
        # Extract title, content and link
        for article in articles:
            date_string = article.find('b').text
            datetime_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
            if from_date <= datetime_obj <= to_date:
                print(date_string)
                title_link = article.find('h4').find('a')
                title = title_link.text.strip()
                link = title_link['href'].lstrip('/')
                content_response = requests.get(f"http://{link}")
                content_soup = BeautifulSoup(
                    content_response.content, 'html.parser')
                content_div = content_soup.find('div', id='Content')
                Content_title = content_soup.find('h1').getText()
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