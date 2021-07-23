# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    name = scrapy.Field()
    salary = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    currency = scrapy.Field()


class HhruItem(scrapy.Item):
    name = scrapy.Field()
    salary = scrapy.Field()
    min_salary = scrapy.Field()
    maх_salary = scrapy.Field()
    currency = scrapy.Field()
    _id = scrapy.Field()
    link = scrapy.Field()
    sourse = scrapy.Field()
