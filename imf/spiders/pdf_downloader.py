import scrapy
from scrapy_playwright.page import PageMethod
import codecs

def should_abort_request(request):


    if request.resource_type == "image" or request.resource_type == "ping" or request.resource_type == "font":
        return True
    
    return False

class PdfDownloaderSpider(scrapy.Spider):
    name = "pdf_downloader"

    custom_settings={
        "PLAYWRIGHT_ABORT_REQUEST" : should_abort_request
    }

    def start_requests(self):
        topics= ['Financial and monetary sector', 'Real sector', 'Fiscal sector', 'External sector', 'Fund operations', 'Cross-sector', 'Economic theory and methods', 'Fund structure and governance', 'Natural resources', 'Environmental policy', 'Environmental sustainability', 'All']
        print('\n\n')
        for index, topic in enumerate(topics, start=1):
            print(f"{index}. {topic}")

        num = input('Select a topic by number: ')

        if(topics[int(num)-1] == 'All'):
            print('Downloading...')
            print('Please wait a few minutes...')
            yield scrapy.Request(
                url='https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50',
                # url='https://www.imf.org/en/Publications/Search#sort=relevancy',
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle'),
                        # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                        # PageMethod('wait_for_timeout', 920000),
                    ]
                )
            )
        elif(int(num) <= len(topics) and int(num) > 0 and topics[int(num)-1] != 'All'):
            print(f'\n\nSelected Item: {topics[int(num)-1]}')
            print('Downloading...')
            print('Please wait a few minutes...')
            yield scrapy.Request(
                url=f'https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50&f:topic=[{topics[int(num)-1]}]',
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle'),
                        # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                        # PageMethod('wait_for_timeout', 920000),
                    ]
                )
            )
        else:
            print('Wrong input...')
            return
        
        '''yield scrapy.Request(
            url='https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50',
            # url='https://www.imf.org/en/Publications/Search#sort=relevancy',
            meta=dict(
            playwright=True,
            playwright_page_methods=[
                PageMethod('wait_for_load_state', 'networkidle'),
                # PageMethod('wait_for_selector', 'ul.coveo-pager-list'),
                # PageMethod('wait_for_timeout', 920000),
            ]
        ))'''

    '''def parse(self, response):
        topics = response.css('div#coveoe60c5b69 ul li')
        result_count = response.css('div.coveo-summary-section span')
        total_items = result_count[-1]
        # print("Count______", total_items.css('.coveo-highlight ::text').get())

        for topic in topics:
            topicText = topic.css('button span.coveo-dynamic-hierarchical-facet-value-label ::text').get()
            print(f"Toipc_________{topicText}")'''

    async def parse(self, response):
        result = response.css('div.CoveoResult')
        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }

        print('(Completed) Thank You')

