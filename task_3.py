"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
записывающую собранные вакансии в созданную БД(добавление данных в БД по ходу сбора данных).

2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой
больше введённой суммы. Необязательно - возможность выбрать вакансии без указанных зарплат

3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""

import json
from pprint import pprint
from time import sleep
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class HH_scraper:
    def __init__(self, url_website, params, headers, host, port, db_name, coll_name):
        self.url_website = url_website
        self.params = params
        self.headers = headers
        self.vacance_data = []
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[coll_name]

    def get_html_string(self, url, params="", headers=""):
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.ok:
                return response.text

        except Exception as e:
            sleep(1)
            print(e)
            return None

    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    def run(self, num_page):
        page = 0
        next_butten = ""
        while (next_butten != None) and (page < num_page):
            if next_butten == "":
                html_string = self.get_html_string(
                    self.url_website + "/search/vacancy", self.params, self.headers
                )
            else:
                html_string = self.get_html_string(next_butten)
            soup = HH_scraper.get_dom(html_string)
            vacance_list = soup.findAll("div", attrs={"class": "vacancy-serp-item"})
            self.get_info_from_element(vacance_list)
            page = int(page) + 1
            try:
                next_butten = (
                    self.url_website
                    + soup.find("a", attrs={"data-qa": "pager-next"}).attrs["href"]
                )
            except Exception as e:
                next_butten = None

    # 3.3 Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
    def write_in_mongo(self, vacance_dict):
        self.collection.update_one(
            {"ссылка на вакансию": vacance_dict["ссылка на вакансию"]},
            {"$set": vacance_dict},
            upsert=True,
        )

    def get_info_from_element(self, vacance_list):

        for vacance in vacance_list:
            vacance_dict = {}
            vacance_name = vacance.find("a", {"class": "bloko-link"}).getText()
            vacance_link = vacance.find("a", {"class": "bloko-link"}).attrs["href"]
            vacance_emp = vacance.find(
                "a", {"class": "bloko-link bloko-link_secondary"}
            ).getText()
            vacance_emp = vacance_emp.replace("\u202f", " ")
            vacance_emp = vacance_emp.replace(" ", " ")
            vacance_city = vacance.find(
                "span", {"data-qa": "vacancy-serp__vacancy-address"}
            ).getText()

            vacance_city = vacance_city.replace("\u202f", " ")
            vacance_dict["наименование вакансии"] = vacance_name
            vacance_dict["ссылка на вакансию"] = vacance_link
            vacance_dict["сайт"] = self.url_website
            vacance_dict["работодатель"] = vacance_emp
            vacance_dict["расположение"] = vacance_city
            self.get_salary(vacance_dict, vacance)
            self.vacance_data.append(vacance_dict)
            self.write_in_mongo(vacance_dict)  # 3.1
            # self.collection.update_one({'ссылка на вакансию': vacance_dict['ссылка на вакансию']},
            #                           {'$set': vacance_dict}, upsert=True)

    def get_salary(self, vacance_dict, vacance):
        try:
            vacance_salary = vacance.find(
                "span", {"data-qa": "vacancy-serp__vacancy-compensation"}
            ).getText()
            vacance_salary = vacance_salary.replace("\u202f", "").split()
            if "–" in vacance_salary:
                vacance_dict["зарплата минимальная"] = float(vacance_salary[0])
                vacance_dict["зарплата максимальная"] = float(vacance_salary[2])
                vacance_dict["валюта"] = vacance_salary[-1]
            elif "от" in vacance_salary:
                vacance_dict["зарплата минимальная"] = float(vacance_salary[1])
                vacance_dict["валюта"] = vacance_salary[-1]
            elif "до" in vacance_salary:
                vacance_dict["зарплата максимальная"] = float(vacance_salary[1])
                vacance_dict["валюта"] = vacance_salary[-1]

        except Exception as e:
            vacance_dict["зарплата"] = None

    # def save_vacance_data(self):
    #     with open("vacancy_hh.json", "w", encoding="utf-8") as file:
    #         json.dump(self.vacance_data, file, indent=2, ensure_ascii=False)


# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной
# платой больше введённой суммы. Необязательно - возможность выбрать вакансии без указанных зарплат


def get_salaty_gr(host, port, db_name, coll_name, input_sum):
    client = MongoClient(host, port)
    db = client[db_name]
    collection = db[coll_name]
    vacances = []
    print(f"Вакансии с зарплатой больше {input_sum}: ")
    for vacancy in collection.find(
        {
            "$or": [
                {"зарплата минимальная": {"$gt": float(input_sum)}},
                {"зарплата максимальная": {"$gt": float(input_sum)}},
            ]
        },
        {
            "наименование вакансии": 1,
            "работодатель": 1,
            "ссылка на вакансию": 1,
            "зарплата минимальная": 1,
            "зарплата максимальная": 1,
            "валюта": 1,
            "_id": 0,
        },
    ):
        vacances.append(vacancy)
    return pprint(vacances)


def get_salaty_null(host, port, db_name, coll_name):
    client = MongoClient(host, port)
    db = client[db_name]
    collection = db[coll_name]
    vacances = []
    print(f"Вакансии с не указанной зарплатой: ")
    for vacancy in collection.find(
        {
            "$or": [
                {
                    "зарплата минимальная": {"$exists": None},
                    "зарплата максимальная": {"$exists": None},
                }
            ]
        },
        {
            "наименование вакансии": 1,
            "работодатель": 1,
            "ссылка на вакансию": 1,
            "_id": 0,
        },
    ):
        vacances.append(vacancy)
    return pprint(vacances)


if __name__ == "__main__":
    str_find = input("Введите вакансию: ")
    num_page = int(input("Введите кол-во страниц: "))

    url_hh = "https://hh.ru"
    params_hh = {
        "area": "1",
        "fromSearchLine": "true",
        "st": "searchVacancy",
        "text": str_find,
        "page": "0",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/91.0.4472.77 Safari/537.36"
    }

    MONGO_HOST = "localhost"
    MONGO_PORT = 27017
    MONGO_DB = "vacancy"
    MONGO_COLL = "vacancy_hh"

    scraper_hh = HH_scraper(
        url_hh, params_hh, headers, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL
    )
    scraper_hh.run(num_page)
    # scraper_hh.save_vacance_data()

    compensation = input(f"Введите минимальный уровень зарплаты: ")
    get_salaty_gr(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL, compensation)
    # get_salaty_null(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL)
