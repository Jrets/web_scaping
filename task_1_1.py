"""
1.Посмотреть документацию к API GitHub, разобраться как вывести список
репозиториев для конкретного пользователя, сохранить JSON-вывод в файле
 *.json; написать функцию, возвращающую список репозиториев.
"""


def repos_github(username):
    import json
    from pprint import pprint

    import requests

    try:
        username = input("Введите имя пользователя github: ")
        url = f"https://api.github.com/users/{username}/repos"
        user_data = requests.get(url)
        list_repos = []
        for i in user_data.json():
            list_repos.append(i["name"])
        # Сохранение списка репозиториев в Json файл
        dict_repos = dict(zip(["name"], [list_repos]))
        with open("repos.json", "w") as f:
            json.dump(json.dumps(dict_repos), f)
        # Вывод списка репозиториев
        pprint(list_repos)
        return list_repos
        # Обработка исключений
    except:
        print("Пользователь не найден")


# Проверка
if __name__ == "__main__":
    repos_github("")
