import requests
from bs4 import BeautifulSoup
import pandas as pd


data = []
#for i in range(1, 2):
    #if i == 1:
url = "https://www.cnbayarea.org.cn/english/News/index.html"
#else:
#url = f"https://www.cnbayarea.org.cn/english/News/index_{i}.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
articles = soup.find_all('h3', class_='gl_list1_t')
# Extract title, link and content
for article in articles:
    link = article.a.get('href')
    title = article.a.text
    content_response = requests.get(f"{link}")
    content_soup = BeautifulSoup(content_response.content, 'html.parser')
    content_div = content_soup.find('div', class_="article_con")
    if content_div:
        paragraphs = content_div.find_all('p', {'style': 'text-align: left;'})
        content = []
        for p in paragraphs:
            content.append(p.get_text())
    else:
        content = ["Content not found."]
    data.append({'Title': title, 'Link': link, 'Content': '\n'.join(content)})

# Export data to Excel
df = pd.DataFrame(data)
df.to_excel('GBA.xlsx', index=False)
