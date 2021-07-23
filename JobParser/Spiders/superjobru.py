import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import HhruItem


class SjruSpider(scrapy.Spider):
    name = "Sjru"
    allowed_domains = ["superjob.ru"]
    start_urls = [
        "https://www.superjob.ru/vacancy/search/"
        "?keywords=Data&geo%5Bt%5D%5B0%5D=4"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            '//a[contains(@class, "f-test-link-Dalshe")]/@href'
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies_links = response.xpath(
            '//div[contains(@class, "f-test-search-result-item")]'
            '//a[contains(@class, "f-test-link")'
            ' and @target="_blank"]/@href'
        ).getall()
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").get()
        item_salary = response.xpath(
            '//div[contains(@class, "f-test-vacancy-base-info")]'
            "/*/following-sibling::*[1]/*/*/*/*/"
            "following-sibling::*[4]/*/*//text()"
        ).getall()
        item_link = response.xpath("//link[@rel='canonical']/@href").get()
        item_sourse = "superjob.ru"
        item = HhruItem(
            name=item_name, salary=item_salary, link=item_link,
            sourse=item_sourse
        )
        yield item
