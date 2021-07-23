import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import HhruItem


class HhruSpider(scrapy.Spider):
    name = "hhru"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://hh.ru/search/vacancy?L_save_area=true"
        "&clusters=true&enable_snippets=true"
        "&text=data+scientist&showClusters=true"
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies_links = response.xpath(
            "//a[@data-qa='vacancy-serp__vacancy-title']/@href"
        ).getall()
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").get()
        item_salary = response.xpath(
            "//p/span[@data-qa='bloko-header-2']/text()"
        ).getall()
        item_link = response.xpath("//link[@rel='canonical']/@href").get()
        item_sourse = "hh.ru"
        item = HhruItem(
            name=item_name, salary=item_salary, link=item_link,
            sourse=item_sourse
        )
        yield item
