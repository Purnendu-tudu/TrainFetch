import requests
from bs4 import BeautifulSoup

url = "https://www.railyatri.in/live-train-status/38705"

page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

result1 = soup.find('div',class_="col-xs-12 lts-timeline_title").find_all('span')


for result in result1:
    print(result.text)

