from scrapy.spiders.init import Spider
from scrapy.http import Request
from scrapy.utils.spider import iterate_spider_output
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.exceptions import CloseSpider
import re

from glassdoor.items.items import CompanyItem


class GlassdoorSpider(Spider):
    name = 'glassdoorspider'
    allowed_domains = ['glassdoor.com']

    index_page = 'https://www.glassdoor.com/index.htm'

    companies_page = 'https://www.glassdoor.com/Reviews/index.htm?overall_rating_low=0&page={}&occ=Software%20Engineer&filterType=RATING_OVERALL'
    start_urls_condition_mapping = {
        companies_page: EC.presence_of_element_located((By.XPATH, "//div[@data-test='employer-card-single']"))
    }

    start_urls_page_mapping = {
        companies_page: "companies"
    }

    start_urls = [*start_urls_condition_mapping]

    page_number = 1

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self._post_init_reqs = self.execute_start_requests()

    def login(self, driver):
        logging.info("-----Login script")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inlineUserEmail"))
        )
        email_input = driver.find_element(By.XPATH, '//input[@id="inlineUserEmail"]')
        email_input.send_keys("your_mail_as_a_djinni_login@gmail.com")
        button = driver.find_element(By.XPATH, '//button[@data-testid="email-form-button"]')
        button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inlineUserPassword"))
        )
        pwd_input = driver.find_element(By.XPATH, '//input[@id="inlineUserPassword"]')
        pwd_input.send_keys("Your password")
        button_submit = driver.find_element(By.XPATH, '//button[@name="submit"]')
        button_submit.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ol[@data-test='community-index-feed-posts']"))
        )

    def start_requests(self):
        return iterate_spider_output(self.init_request())

    def execute_start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            self.page_number = 1;
            condition = self.start_urls_condition_mapping[url]
            formatted_url = url.format(self.page_number)
            page = self.start_urls_page_mapping[url]
            yield Request(formatted_url, dont_filter=True, cb_kwargs={
                "wait_time": 10,
                "wait_until": condition,
                "page": page
            })

    def init_request(self):
        """This function is called before crawling starts."""
        logging.info("-----Initial request")
        yield Request(url=self.index_page, callback=self.initialized, cb_kwargs={"function": self.login})

    def companies_request(self, response, **kwargs):
        """This function is called before crawling starts."""
        logging.info("-----Load companies list")
        yield Request(url=self.companies_page,
                      callback=self.initialized,
                      cb_kwargs={
                          "wait_time": 10,
                          "wait_until": EC.presence_of_element_located(
                              (By.XPATH, "//div[@data-test='employer-card-single']"))})

    def initialized(self, response, **kwargs):
        logging.info("Log in: %s", response)
        return self.__dict__.pop("_post_init_reqs")

    def parse(self, response, **kwargs):
        if response.status == 404:
            raise CloseSpider('Recieve 404 response')
        if kwargs["page"] == "companies":
            return self.parse_companies(response)

    def parse_companies(self, response):
        # stop spider when no quotes found in response
        if len(response.xpath('//div[@data-test="employer-card-single"]')) == 0:
            raise CloseSpider('No quotes in response')

        for company in response.xpath('//div[@data-test="employer-card-single"]'):
            company_item = CompanyItem()
            company_item['name'] = company.xpath('.//div/div[1]/div/div[2]/span/h2/text()').get()
            company_item['rate'] = company.xpath('.//div/div[1]/div/div[2]/span/div/span[1]/b/text()').get()
            company_item['vacancies'] = company.xpath('.//div/div[2]/a[3]/div/h3/text()').get()
            img_url = company.xpath('.//div/div[1]/div/div[1]/img/@src').get()
            company_id = self.get_id(img_url)
            company_item['id'] = company_id
            # //div/div[2]/a[3]/div/h3
            # //*[@id="Explore"]/div[3]/div[1]/div[4]/div[2]/div[1]/div/div[1]/div/div[1]/img
            yield company_item

        # go to next page
        self.page_number += 1
        next_page = self.companies_page.format(self.page_number)
        condition = self.start_urls_condition_mapping[self.companies_page]
        yield response.follow(next_page, callback=self.parse, cb_kwargs={
            "wait_time": 10,
            "wait_until": condition,
            "page": "companies"})

    def get_id(self, img_url):
        if not img_url:
            return None
        result = re.search(r"/(\d+)/", img_url)
        if not result:
            return None
        return result.group(1)
