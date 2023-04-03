# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CandidateItem(Item):
    name = Field()
    email = Field()
    phone = Field()
    telegram=Field()
    skype=Field()
    linkedin = Field()
    github = Field()
    language = Field()
    cv = Field()

