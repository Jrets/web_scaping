"""
1) Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
Для парсинга использовать xpath. Структура данных должна содержать:
- название источника(оригинального источника),
- наименование новости,
- ссылку на новость,
- дата публикации
Нельзя использовать BeautifulSoup
"""

import hashlib
import json
from pprint import pprint

import requests
from lxml import html
from pymongo import MongoClient


def get_news(url_start, headers):
    url_start = url_start
    headers = headers
    response = requests.get(url_start, headers=headers)
    return response


def get_mail(url_start, headers, collection):
    response_news = get_news(url_start, headers)
    dom_block = html.fromstring(response_news.text)
    news_block = dom_block.xpath('//table[@class="daynews__inner"]//a/@href')
    news_dict = {}
    for news in news_block:
        response_news = requests.get(news, headers)
        dom_news = html.fromstring(response_news.text)
        news_dict["sourse"] = dom_news.xpath(
            '//meta[@name="mediator_author"]/@content'
        )[0]
        news_dict["text"] = dom_news.xpath("//h1/text()")[0]
        news_dict["date"] = dom_news.xpath("//span[@datetime]/@datetime")[0]
        news_dict["link"] = news
        write_in_mongo(news_dict, collection)
    return news_dict


def get_lenta(url_start, headers, collection):
    response_news = get_news(url_start, headers=headers)
    dom_block = html.fromstring(response_news.text)
    news_block = dom_block.xpath('//time[contains(@class, "g-time")]/..')
    news_dict = {}
    for news in news_block:
        news_dict["sourse"] = "lenta.ru"
        news_dict["text"] = news.xpath("./text()")[0].replace("\xa0", " ")
        news_dict["date"] = news.xpath(".//@datetime")[0]
        news_dict["link"] = url_start_lenta + news.xpath("./@href")[0]
        write_in_mongo(news_dict, collection)
    return news_dict


def get_yandex(url_start, headers, collection):
    response_news = get_news(url_start, headers=headers)
    dom_block = html.fromstring(response_news.text)
    news_block = dom_block.xpath(
        '//div[contains(@class, "mg-grid__col")]/article[contains(@class, "mg-card")]'
    )
    news_dict = {}
    for news in news_block:
        news_dict["sourse"] = news.xpath(
            './/span[contains(@class, "mg-card-source__source")]//a/text()'
        )[0]
        news_dict["text"] = news.xpath(".//h2/text()")[0].replace("\xa0", " ")
        news_dict["date"] = news.xpath(
            './/span[contains(@class, "mg-card-source__time")]/text()'
        )[0]
        news_dict["link"] = news.xpath(".//a//@href")[0]
        write_in_mongo(news_dict, collection)
    return news_dict


def write_in_mongo(news_dict, collection):
    collection.update_one(
        {"text": news_dict["text"], "date": news_dict["date"]},
        {"$set": news_dict},
        upsert=True,
    )


# inputs data
url_start_mail = "https://news.mail.ru"
url_start_lenta = "https://lenta.ru"
url_start_yandex = "https://yandex.ru/news"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "news"
MONGO_COLL_MAIL = "news_mail"
MONGO_COLL_LENTA = "news_lenta"
MONGO_COLL_YANDEX = "news_yandex"

client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]

collection_mail = db[MONGO_COLL_MAIL]
collection_lenta = db[MONGO_COLL_LENTA]
collection_yandex = db[MONGO_COLL_YANDEX]

# filling the base

get_news_mail = get_mail(url_start_mail, headers, collection_mail)
get_news_lenta = get_lenta(url_start_lenta, headers, collection_lenta)
get_news_yandex = get_yandex(url_start_yandex, headers, collection_yandex)
