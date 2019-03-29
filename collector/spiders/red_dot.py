# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.http import Request
from collector.items.red_dot import RedDotItem
from collector.middlewares.parsefile import ParseFile as PF


class RedDotSpider(scrapy.Spider):
    name = 'red-dot'
    allowed_domains = ['red-dot.org']

    custom_settings = {'ITEM_PIPELINES':{'collector.pipelines.red_dot.RedDotPipline':200}}

    def __init__(self, *args, **kwargs):
        settings = get_project_settings()
        super(RedDotSpider, self).__init__(*args, **kwargs)
        config = settings['CONFIG_FILE']
        self.user_agent = settings['USER_AGENT']
        self.headers = Headers().headers
        self.headers['User-Agent'] = self.user_agent
        self.apis = PF.parse2dict(config, 'apis')
        self.page_number = 0

    def start_requests(self):
        parameters = self.build_parameters(self.page_number)
        url = 'https://www.red-dot.org/index.php?%s' % parameters
        yield Request(url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        data = data['response']['docs']
        item = RedDotItem()
        for d in data:
            item['title'] = d['title']
            item['img_url'] = d['heroImage_stringS']['large']
            item['tags'] = d['subTitle']
            item['prize'] = d['award_stringS']
            item['designer'] = d['credits_stringS']
            item['prize_id'] = 1
            item['evt'] = 5
            item['channel'] = self.name
            item['info'] = {}
            item['info']['description'] = d['description']
            item['info']['juryStatement'] = d['juryStatement_stringS']
            item['info']['website'] = d['web_stringS']
            yield item

        # 更改页码继续爬取
        self.page_number += 1
        parameters = self.build_parameters(self.page_number)
        url = 'https://www.red-dot.org/index.php?%s' % parameters
        if data:
            yield response.follow(url, headers=self.headers, callback=self.parse, dont_filter=True)

    def build_parameters(self, page_number):
        """构造请求参数"""
        parameters = []
        parameters.append('rows=2')
        parameters.append('start={}'.format(page_number))
        parameters.append('eID=tx_solr_proxy')
        parameters.append('L=2')
        parameters.append('id=1')
        parameters.append('grouping=0')
        parameters.append('fq=(altType_stringS:%22Product+Design%22)')
        parameters.append('sort=created+desc')
        parameters = '&'.join(parameters)
        return parameters


class Headers(object):
    headers = {}
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'www.red-dot.org'
    headers['Referer'] = 'https://www.red-dot.org/zh/pd/about/'
    headers['Upgrade-Insecure-Requests'] = 1
