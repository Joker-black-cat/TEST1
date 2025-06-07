# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json


class NikeProjectPipeline:
    def open_spider(self, spider):
        self.file = open('nike_products.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        if not self.first_item:
            line = ',\n' + line
        else:
            self.first_item = False
        self.file.write(line)
        return item
