from scrapy.spiders.init import InitSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest
from djinni.items.items import CandidateItem
import urllib.request
from pathlib import Path
import logging


class DjinniSpider(InitSpider, CrawlSpider):
    counter = 0
    name = 'djinnispider'
    allowed_domains = ['djinni.co']

    login_page = 'https://djinni.co/login?from=frontpage_main'

    storage_mapping = {
        'https://djinni.co/home/inbox/?job_id=492622': "python",  # python vacancy
        'https://djinni.co/home/inbox/?job_id=492130': "front",  # frontend vacancy
        'https://djinni.co/home/inbox/?job_id=491206': "java",  # java vacancy
        'https://djinni.co/home/inbox/?job_id=493377': "qa",  # QA vacancy
        'https://djinni.co/home/inbox/?job_id=493370': "net" # .Net vacancy
    }

    start_urls = [*storage_mapping]

    rules = (
        Rule(LinkExtractor(allow=r'inbox'),
             callback='parse_item'),
    )

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request."""
        token = response.xpath('//*[@name="csrfmiddlewaretoken"]/@value').extract_first()
        return FormRequest.from_response(response,
                                         formdata={'csrf_token': token,
                                                   'password': 'Your password',
                                                   'email': 'your_mail_as_a_djinni_login@gmail.com'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        logging.info("Log in: %s", response)
        return self.initialized()

    def parse_item(self, response):
        # Scrape data from page
        candidate = CandidateItem()
        candidate['name'] = response.xpath('//span[@id="candidate_name"]/text()').get()
        candidate['email'] = self.get_email(response)
        if candidate['email'] == 'magic@djinni.co':
            return None
        candidate['telegram'] = self.get_telegram(response);
        candidate['github'] = response.xpath('//a[starts-with(@href, "https://github.com/")]/@href').get()
        candidate['linkedin'] = response.xpath('//a[contains(@href, "linkedin")]/@href').get()
        candidate['phone'] = self.get_phone(response)

        candidate['language'] = self.get_language(response)
        file_url = response.xpath('//a[starts-with(@href, "https://cv")]/@href').get()
        if file_url:
            try:
                file_name = self.get_file_name(candidate, file_url)
                source = response.request.headers['Referer'].decode("utf-8")
                folder = DjinniSpider.storage_mapping[source]
                path = "/home/andriy/Downloads/CV/" + folder + "/"
                Path(path).mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(file_url, path + file_name)
                candidate['cv'] = file_name
            except Exception as e:
                logging.exception("Cannot download %s Exception: %s", file_url, e)
        DjinniSpider.counter = DjinniSpider.counter + 1
        logging.debug("CV #%s", DjinniSpider.counter)
        return candidate

    def get_phone(self, response):
        phone = response.xpath('//a[starts-with(@href, "tel:")]/text()').get()
        if phone:
            phone = phone.strip()
        return phone

    def get_email(self, response):
        email = response.xpath('//a[@id="candidate_email"]/text()').get()
        if not email:
            email = response.xpath('//a[starts-with(@href, "mailto")]/text()').get()
        if email:
            email = email.strip()
        return email

    def get_telegram(self, response):
        telegram = response.xpath(
            '//a[starts-with(@href, "https://telegram.im/") or starts-with(@href, "https://t.me/") ]/text()').get()
        if telegram:
            telegram = telegram.strip()
        return telegram

    def get_language(self, response):
        language = response.xpath(
            '//span[contains(text(), "language") or contains(text(), "мова")]/strong/text()').get()
        if language:
            language = language.strip()
        return language

    def get_file_name(self, candidate, file_url):
        try:
            original_file_name = file_url[file_url.rfind("/") + 1:]
            ext = original_file_name[original_file_name.rfind("."):]
            if candidate['name']:
                return candidate['name'] + "_" + candidate['email'] + ext
            return candidate['email'] + ext
        except Exception as e:
            return original_file_name

    def parse(self, response, **kwargs):
        pass
