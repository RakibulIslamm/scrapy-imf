import scrapy
from scrapy_playwright.page import PageMethod
import codecs
import math
# from scrapy.crawler import CrawlerProcess
# from scrapy.http.response import Response
from pathlib import Path

def should_abort_request(request):


    if request.resource_type == "image" or request.resource_type == "ping" or request.resource_type == "font":
        return True
    
    return False

class PdfDownloaderSpider(scrapy.Spider):
    name = "pdf_downloader"
    num = None
    topics= ['Financial and monetary sector', 'Real sector', 'Fiscal sector', 'External sector', 'Fund operations', 'Cross-sector', 'Economic theory and methods', 'Fund structure and governance', 'Natural resources', 'Environmental policy', 'Environmental sustainability', 'All']
    custom_settings={
        "PLAYWRIGHT_ABORT_REQUEST" : should_abort_request,
        "PLAYWRIGHT_MAX_CONTEXTS": 20,
        "CONCURRENT_REQUESTS": 32,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 4,
        "CLOSESPIDER_ITEMCOUNT": 1000,
    }

    @classmethod
    def set_num(cls, selected_num):
        cls.num = selected_num

    def start_requests(self):
        print('\n\n')
        for index, topic in enumerate(self.topics, start=1):
            print(f"{index}. {topic}")

        selected_num = input('Select a topic by number: ')
        self.set_num(selected_num)


        if(self.topics[int(self.num)-1] == 'All'):
            print('Downloading...')
            print('Please wait a few minutes...')
            yield scrapy.Request(
                # url='https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50',
                url='https://www.imf.org/en/Publications/Search#sort=relevancy',
                meta=dict(
                    playwright_context = "context-0",
                    playwright_include_page= True,
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle'),
                        # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                        # PageMethod('wait_for_timeout', 920000),
                    ]
                ),
                dont_filter=True,
            )
        elif(int(self.num) <= len(self.topics) and int(self.num) > 0 and self.topics[int(self.num)-1] != 'All'):
            print(f'\n\nSelected Item: {self.topics[int(self.num)-1]}')
            print('Downloading...')
            print('Please wait a few minutes...')
            yield scrapy.Request(
                url=f'https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50&f:topic=[{self.topics[int(self.num)-1]}]',
                meta=dict(
                    playwright=True,
                    playwright_context= "context-1",
                    playwright_include_page= True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle'),
                        # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                        # PageMethod('wait_for_timeout', 920000),
                    ]
                ),
                dont_filter=True,
            )
        else:
            print('Wrong input...')
            return

    

    async def parse(self, response):
        result_count = response.css('div.coveo-summary-section span')
        total_items = result_count[-1]
        items = total_items.css('.coveo-highlight ::text').get()

        result = response.css('div.CoveoResult')
        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }
        # url='https://www.imf.org/en/Publications/Search#first=10&sort=relevancy',


        # Paginating
        items_count = int(items.replace(',', ''))
        if(self.topics[int(self.num)-1] == 'All'):
            if items_count >= 1000:
                for i in range(1, 19):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50',
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                                # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                                # PageMethod('wait_for_timeout', 920000),
                            ]
                        ),
                        dont_filter=True,
                    )
            elif(items_count < 1000 and items_count > 0):
                for i in range(1, math.ceil(items_count/50)):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50',
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                                # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                                # PageMethod('wait_for_timeout', 920000),
                            ]
                        ),
                        dont_filter=True,
                    )
        elif(int(self.num) <= len(self.topics) and int(self.num) > 0 and self.topics[int(self.num)-1] != 'All'):
            pass
        else:
            return

        print("\nPaginating...\n")

    async def parse_rest(self, response):
        page = response.meta["playwright_page"]
        # context_name = response.meta["playwright_context"]
        result = response.css('div.CoveoResult')
        await page.close()
        await page.context.close()
        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }



'''def parse(self, response):
        topics = response.css('div#coveoe60c5b69 ul li')
        result_count = response.css('div.coveo-summary-section span')
        total_items = result_count[-1]
        # print("Count______", total_items.css('.coveo-highlight ::text').get())

        for topic in topics:
            topicText = topic.css('button span.coveo-dynamic-hierarchical-facet-value-label ::text').get()
            print(f"Toipc_________{topicText}")'''

