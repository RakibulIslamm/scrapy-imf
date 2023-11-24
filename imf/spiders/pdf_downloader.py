import scrapy
from scrapy_playwright.page import PageMethod
import codecs

# https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50&f:topic=[Financial and monetary sector]

class PdfDownloaderSpider(scrapy.Spider):
    name = "pdf_downloader"

    topic_filter_arr = []

    def start_requests(self):
        # yield scrapy.Request('https://www.imf.org/en/Publications/Search#sort=relevancy')
        yield scrapy.Request(
            # url='https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50',
            url='https://www.imf.org/en/Publications/Search#sort=relevancy',
            meta=dict(
            playwright=True,
            playwright_page_methods=[
                PageMethod('wait_for_load_state', 'networkidle'),
                # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                # PageMethod('wait_for_timeout', 920000),
            ]
        ))

    '''async def parse(self, response):
        topics = response.css('')'''

    async def parse(self, response):
        result = response.css('div.CoveoResult')

        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(title and link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }


