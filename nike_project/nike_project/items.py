# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NikeProductItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    color = scrapy.Field()
    size = scrapy.Field()
    sku = scrapy.Field()
    details = scrapy.Field()
    img_urls = scrapy.Field()

pass
