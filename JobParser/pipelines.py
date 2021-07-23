# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            min, maх, currency = self.transform_salary_hh(item["salary"])
        else:
            min, maх, currency = self.transform_salary_sj(item["salary"])

        item['min_salary'], item['maх_salary'], item['currency'] = min, maх, currency
        del item["salary"]
        collection = self.mongobase[spider.name]
        collection.update_one({"link": item["link"]}, {"$set": item}, upsert=True)

    def transform_salary_hh(self, salary):
        salary = salary[0].replace('\xa0', '').split(' ')
        if salary[0] == 'до':
            min_salary = None
            max_salary = int(salary[1])
            currency = salary[2][0:3]
        elif salary[2] == 'до':
            min_salary = int(salary[1])
            max_salary = int(salary[3])
            currency = salary[4][0:3]
        elif salary[1] == 'не':
            min_salary = None
            max_salary = None
            currency = None
        else:
            min_salary = int(salary[1])
            max_salary = None
            currency = salary[2][0:3]

        return min_salary, max_salary, currency

    def transform_salary_sj(self, salary):
        if salary[0] == 'от':
            salary = salary[2].replace('\xa0', '')
            min_salary = int(salary[:-4].replace('\xa0', ''))
            max_salary = None
            currency = salary[-4:]
        elif salary[0] == 'до':
            salary = salary[2].replace('\xa0', '')
            min_salary = None
            max_salary = int(salary[:-4].replace('\xa0', ''))
            currency = salary[-4:]
        elif not salary[0]:
            min_salary = None
            max_salary = None
            currency = None
        else:
            min_salary = int(salary[0].replace('\xa0', ''))
            max_salary = int(salary[4].replace('\xa0', ''))
            currency = salary[6]

        return min_salary, max_salary, currency

        return item
