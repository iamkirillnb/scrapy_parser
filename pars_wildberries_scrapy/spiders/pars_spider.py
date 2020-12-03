import scrapy
import datetime

class ItemScrapy(scrapy.Spider):
    name = 'test'
    start_urls = ['https://www.wildberries.ru/catalog/obuv/zhenskaya/sabo-i-myuli/myuli']


    def parse(self, response):
        urls = response.css('a.ref_goods_n_p::attr(href)').extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.get_info)
        next_page = response.css('a.pagination-next::attr(href)').extract_first()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)



    def get_info(self, response):
        current_url = response.xpath('//*[@id="comments_reviews_link"]').attrib['href']
        current_url = current_url[:-9]
        current_url = response.urljoin(current_url)
        color = response.css('span.color::text').get()
        marketing_tags = response.xpath('//*[@id="brandBannerImgRef"]/img').attrib['alt']
        if color is None:
            title = response.css('title::text').get().strip()
        else:
            title = {'name': response.css('title::text').get().strip(), 'color': color}
        current = int(''.join([i for i in response.css('span.final-cost::text').get().split() if i.isdecimal()]))
        original = current
        sale_tag = 0
        if not response.css('span.old-price > del::text').get() is None:
            original = int(''.join([i for i in response.css('span.old-price > del::text').get().split() if i.isdecimal()]))
            sale_tag = round(current * 100 / original)
        stock = False
        if not response.css('link::attr(href)')[-1].get() is None:
            if response.css('link::attr(href)')[-1].get() == 'http://schema.org/InStock':
                stock = True
        main_image = response.xpath('/html/head/meta[5]').attrib['content']
        set_images = response.css('ul.carousel > li > a::attr(href)').getall()
        view360 = ''
        if response.css('li > a > img').attrib['alt'] == 'Трехмерный обзор':
            view360 = response.css('li > a > img').attrib['src']
        description = response.css('div.params > div.pp > span::text').getall()
        metadata = {
            'Material': description[0],
            'description': description[1:-1],
            'country': description[-1]
        }
        yield {
            'timestamp': (datetime.datetime.now()).timestamp(),
            'RPC': response.css('span.j-article::text').get(),
            'url': current_url,
            'title': title,
            'marketing_tags': marketing_tags,
            'brand': response.xpath('//*[@id="brandBannerImgRef"]/*').attrib['alt'],
            'section': response.css('div.product-content-v1 > section > ul > li > a::text').getall(),
            'price_data': {
                'current': current, 'original': original,
                'sale_tag': f'Скидка {sale_tag}'
            },
            'stock': stock,
            'assets': {
                'main_image': main_image,
                'set_images': response.css('ul.carousel > li > a::attr(href)').getall(),
                'view360': view360
            },
            'metadata': metadata
        }

