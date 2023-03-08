import requests
from bs4 import BeautifulSoup
import csv

with open('GBA_Chinese.csv', mode='w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['Title', 'Link', 'Content']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, 2):  # 50 pages
        if i == 1:
            url = "https://www.cnbayarea.org.cn/news/focus/index.html"
        else:
            url = f"https://www.cnbayarea.org.cn/news/focus/index_{i}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for li in soup.select('ul.gl_list1 li'):
            title = li.select_one('h3.gl_list1_t a').text
            link = li.select_one('h3.gl_list1_t a')['href']
            date = li.select_one('span.gl_list_date').text
            content_response = requests.get(f"{link}")
            content_soup = BeautifulSoup(content_response.content, 'html.parser')
            content_div = content_soup.find('div', class_="article_con")
            content_title = content_soup.find('h1', class_="article_t").text
            if content_div:
                paragraphs = content_div.find_all(
                    'p', {'style': 'text-align: justify;'})
                content = []
                for p in paragraphs:
                    if p.text.strip():  # Only include non-empty paragraphs
                        content.append(p.text.strip())
            else:
                content = ["Content not found."]

            # Write row CSV
            writer.writerow({'Title': title, 'Link': link,
                            'Content': '\n'.join(content)})
            



