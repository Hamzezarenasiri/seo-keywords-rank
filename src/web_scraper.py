from urllib.parse import urlparse

import tldextract
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

print(ChromeDriverManager().install())


def get_rank(keyword: str, domain: str, page=1) -> int | None:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    num_in_page = 100
    keyword = keyword.replace(" ", "+")
    driver.implicitly_wait(10)
    if page <= 1:
        url = f"https://www.google.com/search?num={num_in_page}&q={keyword}"
    else:
        url = f"https://www.google.com/search?num={num_in_page}&q={keyword}&start={(page - 1) * num_in_page}"
    driver.get(url)
    search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
    for idx, result in enumerate(search_results, start=1):
        link = result.find_element(By.TAG_NAME, "a")
        parsed_url = urlparse(link.get_attribute("href"))
        # print(f'{idx}-{parsed_url.netloc}')
        if (
            tldextract.extract(parsed_url.netloc).registered_domain
            == tldextract.extract(domain).registered_domain
        ):
            driver.quit()
            return idx
    driver.quit()
    return None
