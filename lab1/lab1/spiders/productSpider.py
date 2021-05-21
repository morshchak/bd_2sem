import scrapy

class ProductSpider(scrapy.Spider):
    name = "products"
    start_urls = ["https://mebli-lviv.com.ua/ua/dyvanu_pryami/"]

    def parse(self, response):
        for product in response.css('div.row.products-row div.product-block.item-default.clearfix'):
            yield {
                'title': product.css('h3.name a::text').extract_first(),
                'price': product.css('div.left span::text').extract_first(),
                'src':   product.css('h3.name a::attr(href)').extract_first(),
                'img': response.urljoin(product.css('div.images img::attr(src)').extract_first())
            }
