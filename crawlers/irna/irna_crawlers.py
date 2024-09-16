import json
import datetime
import jdatetime

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode, urljoin
from db.db_container import DBContainer


class IRNACrawler:
    TOPICS_DATA_FILE = 'topics_data.json'
    BASE_URL = 'https://www.irna.ir/archive'

    def __init__(self, db_container):
        self.topics_data = None
        self.db_container = db_container

    @staticmethod
    def get_web_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enables headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  # For better performance in headless mode

        return webdriver.Chrome(options=chrome_options)

    @staticmethod
    def remove_empty_strings(strings):
        return [item for item in strings if len(item) != 0]

    def get_topics_data(self):
        with open(self.TOPICS_DATA_FILE, 'r') as topics_file:
            self.topics_data = json.load(topics_file)

    def run(self):
        self.get_topics_data()
        for topic_idx in self.topics_data:
            self.get_list_of_news(topic=topic_idx,
                                  date=datetime.datetime.now())
            break

    def get_list_of_news(self, topic, date):
        page_number = 1
        news_links = set({})
        jalali_date = jdatetime.date.fromgregorian(date=date)

        params = {
            'pi': str(page_number),
            'tp': str(topic),
            'ms': '0',
            'dy': str(jalali_date.day),
            'mn': str(jalali_date.month),
            'yr': str(jalali_date.year)
        }

        while True:
            fetched_news_links = self.get_page_news_list(params)
            fresh_links = {
                news_link for news_link in fetched_news_links if news_link not in news_links
            }
            if len(fresh_links) == 0:
                break

            news_links = news_links.union(fetched_news_links)
            page_number += 1
            params['pi'] = str(page_number)

            batch = [{
                'topic': str(topic),
                'date': date,
                'news_link': link}
                for link in fresh_links]
            self.db_container.batch_insert_news_links(batch)

    def get_page_news_list(self, params):

        query_string = urlencode(params)
        full_url = urljoin(self.BASE_URL, "?" + query_string)

        driver = self.get_web_driver()
        driver.get(full_url)
        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        news_items = soup.find_all('li', class_='news')
        news_links = set({})

        for news_item in news_items:
            a_tags = news_item.find_all('a')

            for a in a_tags:
                href = a.get('href')
                news_links.add(href)

        return news_links


if __name__ == '__main__':
    IRNACrawler(db_container=DBContainer(
        user='postgres',
        password='postgres',
        host='localhost',
        port='15432',
        database='persian-news'
    )).run()
