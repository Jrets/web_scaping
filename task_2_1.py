"""
Необходимо собрать информацию о вакансиях на вводимую должность (используем input) с сайтов
 Superjob(необязательно) и HH(обязательно). Приложение должно анализировать несколько страниц
  сайта (также вводим через input).
Получившийся список должен содержать в себе минимум:
1) Наименование вакансии.
2) Предлагаемую зарплату (отдельно минимальную и максимальную).
3) Ссылку на саму вакансию.
4) Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов. Сохраните результат в json-файл
"""

import json
from pprint import pprint
from time import sleep

import requests
from bs4 import BeautifulSoup


class HH_scraper:
    def __init__(self, url_website, params, headers):
        self.url_website = url_website
        self.params = params
        self.headers = headers
        self.vacance_data = []

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

    def save_vacance_data(self):
        with open("vacancy_hh.json", "w", encoding="utf-8") as file:
            json.dump(self.vacance_data, file, indent=2, ensure_ascii=False)


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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    }

    scraper_hh = HH_scraper(url_hh, params_hh, headers)
    scraper_hh.run(num_page)
    scraper_hh.save_vacance_data()
