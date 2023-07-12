# parse all images from this site https://rozetka.com.ua/notebooks/c80004/

import requests
from bs4 import BeautifulSoup
from app import db, app, laptop
import random


def data_parse(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    image_tags = soup.find_all('img')
    image_urls = []

    for img in image_tags:
        if 'src' in img.attrs:
            image_urls.append([
                img['src'],
                img['alt']
            ])
    image_urls = [url for url in image_urls if url[0].endswith('.jpg')]

    with app.app_context():
        for img in image_urls:
            laptops = laptop.query.filter_by(label=img[1]).all()
            if len(laptops) > 0:
                continue
            l = laptop(
                label=img[1],
                price=random.randint(30, 50) * 1000,
                image=img[0],
            )
            db.session.add(l)
            db.session.commit()


urls = [
    # "https://rozetka.com.ua/dvd-hd-players/c80011/",
    # "https://rozetka.com.ua/mobile-phones/c80003/producer=samsung;series=galaxy-s/",
    # "https://rozetka.com.ua/mobile-phones/c80003/",
    # "https://rozetka.com.ua/tablets/c130309/,"
    # "https://rozetka.com.ua/projector/c80012//",
    "https://rozetka.com.ua/computers/c80095/page=1/"
    "https://rozetka.com.ua/computers/c80095/page=2/"
    "https://rozetka.com.ua/computers/c80095/page=3/"
    "https://rozetka.com.ua/computers/c80095/page=4/"
    "https://rozetka.com.ua/computers/c80095/page=5/"
    "https://rozetka.com.ua/computers/c80095/page=6/"
    "https://rozetka.com.ua/computers/c80095/page=7/"
    "https://rozetka.com.ua/computers/c80095/page=8/"
    "https://rozetka.com.ua/computers/c80095/page=9/"
    "https://rozetka.com.ua/computers/c80095/page=10/"
    "https://rozetka.com.ua/computers/c80095/page=11/"

]

for url in urls:
    data_parse(url)
