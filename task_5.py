import time
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

#предварительные ласки
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "vc"
MONGO_COLLECTION = "tokyofashion"
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

chrome_options = Options()
chrome_options.add_argument("start-maximized")
CHROMEDRIVER_PATH = "../chromedriver"

find_teg = input("Введите текст для поиска: ")
time.sleep(10)

driver = webdriver.Chrome(options=chrome_options, executable_path=CHROMEDRIVER_PATH)

driver.get("https://vk.com/tokyofashion/")

#переход в группу и поиск текста
def find_text(inp_text):
    elem = driver.find_element_by_class_name("ui_tab_sel")
    elem.click()
    time.sleep(int(3))
    elem = driver.find_element_by_xpath('//input[@type="text" and @id="wall_search"]')
    time.sleep(int(3))
    elem.click()
    elem.send_keys(inp_text)
    elem.send_keys(Keys.ENTER)

#скролл страницы и закрытие окна регистрации
def scroll_post(count_scroll, time_sleep, collection):
    for i in range(int(count_scroll)):
        time.sleep(int(time_sleep))
        posts = driver.find_elements_by_class_name("_post")
        actions = ActionChains(driver)
        actions.move_to_element(posts[-1])
        actions.perform()
        while True:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(text(),'Не сейчас')]")
                    )
                )
                button.click()
            except:
                break
    time.sleep(int(3))
    posts_path = '//div[contains(@class, "_post post page_block post--with-likes")]'
    posts = driver.find_elements_by_xpath(posts_path)
    posts_list = []
    for post in posts:
        post_info = {}
        try:
            date = post.find_element_by_class_name("rel_date")
            text = post.find_element_by_class_name("wall_post_text")
            link = post.find_element_by_class_name("post_link")
            likes = post.find_element_by_class_name("_like")
            shares = post.find_element_by_class_name("_share")
            views = post.find_element_by_class_name("like_views")
            post_info["date"] = date.text
            post_info["text"] = text.text.replace("\n", " ")
            post_info["link"] = link.get_attribute("href")
            post_info["likes"] = likes.get_attribute("data-count")
            post_info["shares"] = shares.get_attribute("data-count")
            post_info["views"] = views.text
        except Exception as e:
            None
        write_in_mongo(post_info, collection)
        posts_list.append(post_info)
    return posts_list

#запись в БД просточно, с исключением дублей
def write_in_mongo(post_info, collection):
    collection.update_one({"link": post_info["link"]}, {"$set": post_info}, upsert=True)


find_post = find_text(find_teg)
scroll = scroll_post(3, 3, collection)
