# -*- coding: utf-8 -*-
import scrapy
import requests
from urllib.parse import urljoin
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from collector.middlewares.browser import Browser
from collector.middlewares.parsefile import ParseFile as PF
from collector.middlewares.redishandle import RedisHandle
from collector.items.xiaomiyoupin import XiaomiyoupinItem


class Headers(object):
    headers = {}
    headers['Accept'] = 'text/html,application/xhtml+xm…ml;q=0.9,image/webp,*/*;q=0.8'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
    headers['Connection'] = 'keep-alive'
    headers['Host'] = 'www.xiaomiyoupin.com'

    post_headers = {}
    post_headers['Host'] = 'www.xiaomiyoupin.com'
    post_headers['Accept'] = '*/*'
    post_headers['Referer'] = 'https://www.xiaomiyoupin.com'
    post_headers['Origin'] = 'https://www.xiaomiyoupin.com'
    post_headers['Content-Length'] = '364'


class XiaomiyoupinSpider(scrapy.Spider):
    name = 'xiaomiyoupin'
    allowed_domains = ['xiaomiyoupin.com']
    start_url = 'https://www.xiaomiyoupin.com/'

    custom_settings ={
        'ITEM_PIPELINES':{'collector.pipelines.xiaomiyoupin.XiaomiyoupinPipline': 100}}

    def __init__(self, *args, **kwargs):
        settings = get_project_settings()
        super(XiaomiyoupinSpider, self).__init__(*args, **kwargs)
        config = settings['CONFIG_FILE']
        self.headers = Headers().headers
        self.user_agent = settings['USER_AGENT']
        self.host = PF.parse2dict(config, 'redis')['host']
        self.port = PF.parse2dict(config, 'redis')['port']
        self.temp = settings['TEMP_DIR']
        self.ext = lambda d, r: Selector(text=d).xpath(r).extract()
        self.ext_fst = lambda d, r: Selector(text=d).xpath(r).extract_first()
        self.headers['User-Agent'] = self.user_agent

    def start_requests(self):
        phantomjs = Browser.phantomjs(self.user_agent)
        phantomjs.get(self.start_url)
        # 等待分类列表加载完成
        WebDriverWait(phantomjs, 60).until(
            lambda b: b.find_elements_by_css_selector('.nav-item '))
        data = phantomjs.page_source
        phantomjs.quit()

        rules = Rules().homepage
        # 选择需要提取数据的HTML块
        block = self.ext_fst(data, rules['block'])
        categorys = self.ext(block, rules['categorys'])
        links = self.ext(block, rules['links'])
        for cry, link in zip(categorys, links):
            meta = {'category':cry}
            url = urljoin(self.start_url, link)
            yield Request(url, headers=self.headers, meta=meta, callback=self.parse)

    def parse(self, response):
        RH = RedisHandle(self.host, self.port)
        item = XiaomiyoupinItem()
        phantomjs = Browser.phantomjs(self.user_agent)
        phantomjs.get(response.url)
        # 等待商品列表加载完成
        WebDriverWait(phantomjs, 60, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.typeGoods-item')))
        data = phantomjs.page_source
        phantomjs.quit()

        rules = Rules().good_list
        # 商品子类别块
        block = self.ext(data, rules['block'])
        for b in block:
            sub_category = self.ext_fst(b, rules['sub_category'])
            titles = self.ext(b, rules['titles1']) + self.ext(b, rules['titles2'])
            links = self.ext(b, rules['links1']) + self.ext(b, rules['links2'])
            prices = self.ext(b, rules['prices1']) + self.ext(b, rules['prices2'])
            for title, link, price in zip(titles, links, prices):
                if RH.verify(self.name, urljoin(response.url, link)):
                    continue
                gid = int(link.split('=')[-1])
                comment = self.get_comments(gid)
                item['category'] = response.meta['category']
                item['sub_category'] = sub_category
                item['url'] = urljoin(response.url, link)
                item['title'] = title
                item['price'] = price
                item['comment_count'] = comment['comment_count']
                item['favorable_rate'] = comment['favorable_rate']
                item['star_level'] = comment['star_level']
                yield item

    def get_comments(self, gid):
        # 请求接口获取评论数据信息
        url = 'https://www.xiaomiyoupin.com/app/shopv3/pipe'
        headers = Headers().post_headers
        headers['User-Agent'] = self.user_agent
        # 构造请求参数
        ov = '{"model":"Product", "action":"CommentIndexV2", "parameters":{"gid":%d}}' % gid
        p = '{"index_type":0, "gid":%d, "pindex":1, "psize":10, "tag_name":null}' % gid
        lt = '{"model":"Product", "action":"CommentListOnly", "parameters":%s}' % p
        parameters = '{"overView":%s, "list":%s}' % (ov, lt)

        response = requests.post(url, data=parameters, headers=headers).json()
        data = response['result']['overView']['data']
        rst = {}
        rst['comment_count'] = data['tags'][0]['count']
        rst['favorable_rate'] = data['positive_rate']
        rst['star_level'] = data['avg_score']
        return rst


class Rules(object):

    # 主页
    homepage = {}
    homepage['block'] = '//div[@class="nav-container"]'
    homepage['categorys'] = '//li[@class="nav-item "]//span/a/text()'
    homepage['links'] = '//li[@class="nav-item "]//span/a/@data-src'

    # 商品列表页面
    good_list = {}
    good_list['block'] = '//div[@class="typeGoods-item"]'
    good_list['sub_category'] = '//h2/text()'
    good_list['titles1'] = '//div[@class="pro-item m-tag-a first"]//p[@class="pro-info"]/@title'
    good_list['titles2'] = '//div[@class="pro-item m-tag-a "]//p[@class="pro-info"]/@title'
    good_list['links1'] = '//div[@class="pro-item m-tag-a first"]/@data-src'
    good_list['links2'] = '//div[@class="pro-item m-tag-a "]/@data-src'
    good_list['prices1'] = '//div[@class="pro-item m-tag-a first"]//p[@class="pro-price"]//span[@class="m-num"]/text()'
    good_list['prices2'] = '//div[@class="pro-item m-tag-a "]//p[@class="pro-price"]//span[@class="m-num"]/text()'
