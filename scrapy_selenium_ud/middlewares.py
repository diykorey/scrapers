"""This module contains the ``ScrapersMiddleware`` scrapy middleware"""

import undetected_chromedriver as uc
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait


class ScrapersMiddleware:
    """Scrapy middleware handling the requests using selenium"""

    def __init__(self, driver):
        self.driver = driver

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        options = ChromeOptions()
        options.add_argument('--headless')
        options.page_load_strategy = 'none'
        driver = uc.Chrome(options=options)

        middleware = cls(
            driver=driver
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        self.driver.get(request.url)

        wait_until = request.cb_kwargs.get("wait_until")
        if wait_until:
            wait_time = request.cb_kwargs.get("wait_time")
            WebDriverWait(self.driver, wait_time).until(
                wait_until
            )

        body = str.encode(self.driver.page_source)
        function = request.cb_kwargs.get("function")
        if function:
            function(self.driver)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""

        self.driver.quit()
