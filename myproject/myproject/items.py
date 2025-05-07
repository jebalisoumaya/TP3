# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

class MyprojectItem(scrapy.Item):
    # Define the fields for your item here:
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()