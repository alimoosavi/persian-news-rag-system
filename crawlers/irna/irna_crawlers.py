import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode, urljoin


class IRNACrawler:
    TOPICS_DATA_FILE = 'topics_data.json'
    BASE_URL = 'https://www.irna.ir/archive'

    def __init__(self):
        self.topics_data = None

    @staticmethod
    def get_web_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enables headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  # For better performance in headless mode

        return webdriver.Chrome(options=chrome_options)

    def get_topics_data(self):
        with open(self.TOPICS_DATA_FILE, 'r') as topics_file:
            self.topics_data = json.load(topics_file)

    def fetch_content(self):
        params = {
            'pi': '1',
            'tp': '1003064',
            'ms': '0',
            'dy': '24',
            'mn': '6',
            'yr': '1403'
        }
        query_string = urlencode(params)
        full_url = urljoin(self.BASE_URL, "?" + query_string)

        driver = self.get_web_driver()
        driver.get(full_url)
        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <li> elements with class="news"
        news_items = soup.find_all('li', class_='news')

        # Iterate over each <li> element and extract href links from <a> tags
        for news_item in news_items:
            # Find all <a> tags within the current <li> element
            a_tags = news_item.find_all('a')

            # Extract and print the href attributes from each <a> tag
            for a in a_tags:
                href = a.get('href')
                print(href)


if __name__ == '__main__':
    IRNACrawler().fetch_content()
