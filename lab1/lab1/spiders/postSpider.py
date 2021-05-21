import scrapy


class PostSpider(scrapy.Spider):
    name = "posts"
    start_urls = [
        "http://www.justjared.com/",
        "http://www.justjared.com/page/2/"
    ]

    def parse(self, response):
        for post in response.xpath("//div[@class='post']"):
            yield {
                'url': response.url,
                'text': post.xpath(".//div[@class='entry']/p/text()").extract(),
                'images': post.xpath(".//div[@class='lead-img']/img/@src").extract()
            }

        for a in response.xpath("//h2").xpath(".//a"):
            yield response.follow(a, callback=self.parse)