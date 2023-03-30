# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BaseItem(Item):
    _id = Field()
    crawled_timestamp = Field()


class CareerHubItem(BaseItem):
    # just need one field, cause the structure of the item is dynamic
    item = Field()
