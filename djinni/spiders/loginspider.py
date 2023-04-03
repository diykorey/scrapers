from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser

#just Djinni log in flow sample
class LoginSpider(Spider):
    name = 'loginspider'
    start_urls = ['https://djinni.co/login?from=frontpage_main']

    def parse(self, response):
        token = response.xpath('//*[@name="csrfmiddlewaretoken"]/@value').extract_first()

        return FormRequest.from_response(response,
                                         formdata={'csrf_token': token,
                                                   'password': 'Your password',
                                                   'email': 'your_mail_as_a_djinni_login@gmail.com'},
                                         callback=self.scrape_pages)

    def scrape_pages(self, response):
        super().parse(response)
