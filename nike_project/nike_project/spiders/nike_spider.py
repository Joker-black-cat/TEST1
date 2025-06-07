import scrapy
import json
from nike_project.items import NikeProductItem
from urllib.parse import quote, urlencode

class NikeProductsSpider(scrapy.Spider):
    name = 'nike_products'
    allowed_domains = ['www.nike.com.cn',"api.nike.com.cn"]
    start_urls = ['https://www.nike.com.cn/w/']
    item_count = 0
    page_count = 24
    max_items = 48
    anonymousId = "DSWXE2F6A7E615766ABA35DAC6810106D336"  

    def parse(self, response):
        channelId = json.loads(response.css('#__NEXT_DATA__::text').get())['props']['pageProps']['initialState']['Config']['channelId']
        base_url = "https://api.nike.com.cn/cic/browse/v2"
        params = {
            "queryid": "products",
            "anonymousId": self.anonymousId,
            "country": "cn",
            "language": "zh-Hans",
            "endpoint": "",
            "localizedRangeStr": "{lowestPrice} — {highestPrice}"
        }
        
        for anchor in range(0, self.max_items, self.page_count): 
            params["endpoint"] = f"/product_feed/rollup_threads/v2?filter=marketplace(CN)&filter=language(zh-Hans)&filter=employeePrice(true)&anchor={anchor}&consumerChannelId={channelId}&count=24"
            encoded_endpoint = quote(params["endpoint"], safe="")
            page_url = f"{base_url}?{urlencode(params)}"
            # self.logger.info(f"Fetching page: {page_url}")

            yield response.follow(page_url, callback=self.parse_page)

    def parse_page(self, response):
        products =  response.json()['data']['products']['products']
        if not products:
            self.logger.info("No products found on this page.")
            return
        unique_links = set()

        for product in products:
            link = product['colorways'][0]['pdpUrl'].replace("{countryLang}", "https://www.nike.com.cn").strip()
            if len(unique_links) >= self.max_items:
                break
            unique_links.add(link)

        for link in unique_links:
            if self.item_count >= self.max_items:
                break
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response):
        
        response_data = json.loads(response.css('#__NEXT_DATA__::text').get())

        if not response_data:
            self.logger.warning(f"Response data is empty for URL: {response.url}")
            return

        item = NikeProductItem()
        item['url'] = response.url.strip()
        self.logger.info(keys:=response_data['props']['pageProps'].keys())
        if colorwayImages:=response_data['props']['pageProps'].get('colorwayImages',""):
            styleColor = colorwayImages[0]['styleColor'].strip()
            globalProductId = colorwayImages[0]['globalProductId'].strip()
            product = response_data['props']['pageProps']['productGroups'][0]['products'][styleColor]

            item['title'] = colorwayImages[0]['altText'].strip()
            item['price'] = response_data['props']['pageProps']['locale']['currencySymbol'] + str(product['prices']['currentPrice'])

            # 颜色信息
            item['color'] =  product['colorDescription'].strip()

            # 尺码信息
            sizes = product['sizes']
            item['size'] = [f"{x.get("localizedLabelPrefix","")} {x.get("localizedLabel","")}".strip() for x in sizes] if sizes else '暂无尺码'

            # SKU信息
            item['sku'] = styleColor.strip()

            # 详情描述
            try:
                item['details'] = product['productInfo']['productDetails'][0]['body']
            except (IndexError, KeyError):
                self.logger.warning(product['productInfo']['productDetails'])
                item['details'] = '暂无详情描述'
            # 图片URL
            large_img="t_PDP_1728_v1/f_auto,q_auto:eco"
            
            item['img_urls']=[]
            contentImages = product['contentImages']
            for img in contentImages:
                try:
                    item['img_urls'].append(img['properties']['squarish']['url'].replace("t_default",large_img))
                except (IndexError, KeyError, TypeError, AttributeError):
                    self.logger.info(img)

        else:
            key = "initialstate" if "initialstate" in keys else "initialState"
            pbid = response_data['query']['pbid']
            product = response_data['props']['pageProps'][key]["Threads"]['products'][pbid]
            item['title']=product["fullTitle"]
            item['price'] = response_data['props']['pageProps'][key]['localization']['currencySymbol'] + str(product['currentPrice'])

            # 颜色信息
            item['color'] =  product['colorDescription'].strip()

            # 尺码信息
            sizes = product['skus']
            item['size'] = [f"{x.get("localizedLabelPrefix","")} {x.get("localizedSize","")}".strip() for x in sizes] if sizes else '暂无尺码' #x['localizedLabelPrefix']+x['localizedLabel']

            # SKU信息
            item['sku'] = product["styleColor"].strip()

            # 详情描述
            details = product['nbyContentCopy']['moreDescriptions']
            if details:
                merged_body = []
                for detail in details:
                    try:                
                        merged_body.extend(detail["body"])                 
                    except (IndexError, KeyError):
                        self.logger.info(detail)
                item['details'] = merged_body
            else:
                item['details'] = '暂无详情描述'
            large_img="t_PDP_1728_v1/f_auto,q_auto:eco"
            
            item['img_urls']=[]
            contentImages = product['nodes'][0]['nodes']
            for img in contentImages:
                try:
                    item['img_urls'].append(img['properties']['squarish']['url'].replace("t_default",large_img))
                except (IndexError, KeyError, TypeError, AttributeError):
                    self.logger.info(img)

        self.item_count += 1

        yield item
