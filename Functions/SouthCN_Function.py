import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

def Extract_SouthCN_date(from_date: datetime, to_date: datetime):
    with open('SouthCN.csv', mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Link', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        i = 0
        datetime_obj = to_date
        while from_date <= datetime_obj:
            i += 1
            url = f"https://www.southcn.com/node_b5769d65fb?cms_node_post_list_page={i}"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('div', class_="itm j-link")
            for article in articles:
                date_string = article.find("div", class_="time").text
                datetime_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
                if from_date <= datetime_obj <= to_date:
                    print(datetime_obj)
                    title = article.find("h3").text.strip()
                    link = article.find("a")['href']
                    content_response = requests.get(f"{link}")
                    content_soup = BeautifulSoup(content_response.content, 'html.parser')
                    content_div = content_soup.find('div', class_="m-article")
                    content_title = content_div.find(id_="article_title")
                    if content_div:
                        paragraphs = content_div.find_all(
                            'p', {'style': 'text-align: justify;'})
                        content = []
                        for p in paragraphs:
                            if p.text.strip():  # Only include non-empty paragraphs
                                content.append(p.text.strip())
                        else:
                            content = ["No Text Content"]
                    else:
                        content = ["Content not found."]

                    # Write row CSV
                    writer.writerow({'Title': title, 'Link': link,'Content': '\n'.join(content)
                                    })
                    
def Extract_SouthCN_all():
    with open('SouthCN.csv', mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Link', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, 101):  # 100 pages
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
                        content = ["No Text Content"]
                else:
                    content = ["Content not found."]

                # Write row CSV
                writer.writerow({'Title': title, 'Link': link,
                                'Content': '\n'.join(content)})
            
                    
#Example
today = datetime.today()
from_date = datetime.combine(today - timedelta(days=1), time.min)
to_date = datetime.combine(today, time.max) - timedelta(seconds=1)

Extract_SouthCN_date(from_date, to_date)

#Extract_SouthCN_all()

