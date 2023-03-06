import requests
from bs4 import BeautifulSoup
import csv

with open('GBA_English.csv', mode='w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['Title', 'Link', 'Content']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, 21):  # 20 pages
        if i == 1:
            url = "https://www.cnbayarea.org.cn/english/News/index.html"
        else:
            url = f"https://www.cnbayarea.org.cn/english/News/index_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('h3', class_='gl_list1_t')

        for article in articles:
            link = article.a.get('href')
            title = article.a.text
            content_response = requests.get(f"{link}")
            content_soup = BeautifulSoup(
                content_response.content, 'html.parser')
            content_div = content_soup.find('div', class_="article_con")
            if content_div:
                paragraphs = content_div.find_all(
                    'p', {'style': 'text-align: left;'})
                content = []
                for p in paragraphs:
                    if p.text.strip():  # Only include non-empty paragraphs
                        content.append(p.text.strip())
            else:
                content = ["Content not found."]

            # Write row CSV
            writer.writerow({'Title': title, 'Link': link,
                            'Content': '\n'.join(content)})
