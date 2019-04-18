# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings


class Headers(object):
    headers = {}
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'www.g-mark.org'
    headers['Referer'] = 'http://www.g-mark.org/'
    headers['Upgrade-Insecure-Requests'] = 1


class GMarkSpider(scrapy.Spider):
    name = 'g-mark'
    allowed_domains = ['g-mark.org']

    def __init__(self, *args, **kwargs):
        settings = get_project_settings()
        super(GMarkSpider, self).__init__(*args, **kwargs)
        self.user_agent = settings['USER_AGENT']
        self.headers = Headers().headers
        self.headers['User-Agent'] = self.user_agent
        self.ext = lambda d, r: Selector(text=d).xpath(r).extract()
        self.ext_fst = lambda d, r: Selector(text=d).xpath(r).extract_first()

    def start_requests(self):
        url = 'http://www.g-mark.org/award/'
        yield Request(url, headers=self.headers, dont_filter=True, callback=self.parse)

    def parse(self, response):
        data = response.body.decode('utf-8', 'ignore')
        rules = Rules().parse
        years = self.ext(data, rules['years'])[1:]
        for year in years:
            meta = {'year':year}
            meta['dont_filter'] = True
            url = 'http://www.g-mark.org/award/search?from={}'.format(year)
            yield Request(url, headers=self.headers, meta=meta, callback=self.parse_list)
            break

    def parse_list(self, response):
        data = response.body.decode('utf-8', 'ignore')
        rules = Rules().parse_list
        links = self.ext(data, rules['links'])
        for link in links:
            url = response.urljoin(link)
            yield Request(url, headers=self.headers, meta=response.meta,
                          callback=self.parse_details)
            break

        next_page = self.ext_fst(data, rules['next_page'])
        if next_page:
            yield response.follow(next_page, headers=self.headers, meta=response.meta,
                                  callback=self.parse_list)

    def parse_details(self, response):
        data = response.body.decode('utf-8', 'ignore')
        rules = Rules().parse_details
        basic_info = self.ext(data, rules['basic_info'])
        #basic_info = [ i for i in basic_info if  ]
        #print(basic_info)


class Rules(object):
    parse = {}
    parse['years'] = '//select[@id="selectyear01"]//option/@value'

    parse_list = {}
    parse_list['links'] = '//ul[@class="itemList listA"]//li/a[@data-pjax="#result"]/@href'
    parse_list['next_page'] = '//div[@class="morebtn"]/a/@href'

    parse_details = {}
    parse_details['basic_info'] = '//dl[@class="basicinfo"]//text()'
