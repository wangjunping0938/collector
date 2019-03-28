# -*- coding: utf-8 -*-
#
# 百度搜索热度爬虫
import sys
import scrapy
import string
from urllib.parse import quote
from scrapy.utils.project import get_project_settings
from scrapy.http import Request
from scrapy.selector import Selector
from collector.middlewares.interface import Interface as I
from collector.middlewares.parsefile import ParseFile as PF
from collector.middlewares.redishandle import RedisHandle
from collector.items.baiduhot import BaiduhotItem


class Headers(object):
    headers = {}
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    headers['Accept-Encoding'] = 'gzip, deflate'
    headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
    headers['Cache-Control'] = 'max-age=0'
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'www.baidu.com'
    headers['Upgrade-Insecure-Requests'] = 1


class BaiduhotSpider(scrapy.Spider):
    name = 'baiduhot'
    allowed_domains = ['baidu.com']
    # 指定当前爬虫数据处理程序
    custom_settings ={
        'ITEM_PIPELINES':{'collector.pipelines.baiduhot.BaiduhotPipline': 100}}

    def __init__(self, mode=None, *args, **kwargs):
        settings = get_project_settings()
        super(BaiduhotSpider, self).__init__(*args, **kwargs)
        config = settings['CONFIG_FILE']
        self.host = PF.parse2dict(config, 'redis')['host']
        self.port = PF.parse2dict(config, 'redis')['port']
        # 配置文件中的API接口地址
        self.apis = PF.parse2dict(config, 'apis')
        self.headers = Headers().headers
        self.user_agent = settings['USER_AGENT']
        self.mode = mode

    def start_requests(self):
        RH = RedisHandle(self.host, self.port)

        if self.mode:
            api = self.apis['opalus_queue_list']
            companys = I.company_queue_list(api, 'bd_status')
        else:
            api = self.apis['opalus_company_list']
            companys = I.company_list(api)

        for c in companys:
            api = self.apis['opalus_company_view']
            details = I.company_view(api, c)
            keywords = set([details['name'], details['short_name']])
            for keyword in keywords:
                link = 'http://www.baidu.com/s?wd={}'.format(keyword)
                link = quote(link, safe=string.printable, encoding='gb2312')
                c['link'] = link
                # Redis中验证当前连接是否被爬取
                if RH.verify(self.name, link):
                    continue
                meta = {'dont_filter':True}
                meta['keyword'] = keyword
                meta['company'] = c
                yield Request(link, meta=meta, headers=self.headers, callback=self.parse)

    def parse(self, response):
        data = response.body.decode('utf-8', 'ignore')
        rules = eval('Rules().{}'.format(sys._getframe().f_code.co_name))
        item = BaiduhotItem()
        ext=lambda d, r: int(''.join(Selector(text=d).xpath(r).re(r'\d+')))

        # 基本信息
        company = response.meta['company']
        item['name'] = company['name']
        item['number'] = company['number']
        item['company'] = company

        keyword = response.meta['keyword']
        if keyword == company['name']:
            try:
                item['baidu_hot'] = ext(data, rules['baidu_hot'])
            except ValueError:
                item['baidu_hot'] = 0
        else:
            try:
                item['baidu_brand_hot'] = ext(data, rules['baidu_brand_hot'])
            except ValueError:
                item['baidu_brand_hot'] = 0
        yield item


class Rules(object):
    parse = {}
    parse['baidu_hot'] = '//div[@class="nums"]//span[@class="nums_text"]/text()'
    parse['baidu_brand_hot'] = '//div[@class="nums"]//span[@class="nums_text"]/text()'
