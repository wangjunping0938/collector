# -*- coding: utf-8 -*-
#
# https://www.tianyancha.com spider
import os
import sys
import time
import random
import logging
import traceback
import scrapy
import requests
from urllib.request import urlretrieve
from PIL import Image
from pyvirtualdisplay import Display
from scrapy.utils.project import get_project_settings
from scrapy.http import Request
from scrapy.selector import Selector
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from collector.middlewares.browser import Browser
from collector.middlewares.parsefile import ParseFile as PF
from collector.middlewares.redishandle import RedisHandle
from collector.middlewares.interface import Interface as I
from collector.items.tianyancha import TianyanchaItem


class Headers(object):
    headers = dict()
    headers['Host'] = 'www.tianyancha.com'
    headers['Referer'] = 'https://www.tianyancha.com/login'
    headers['X-Requested-With'] = 'XMLHttpRequest'


class TianyanchaSpider(scrapy.Spider):
    name = 'tianyancha'
    allowed_domains = ['tianyancha.com']

    # 设置爬取数据处理程序
    custom_settings ={
        'ITEM_PIPELINES':{'collector.pipelines.tianyancha.TianyanchaPipline': 100}}

    def __init__(self, mode=None, *args, **kwargs):
        settings = get_project_settings()
        super(TianyanchaSpider, self).__init__(*args, **kwargs)
        config = settings['CONFIG_FILE']
        self.host = PF.parse2dict(config, 'redis')['host']
        self.port = PF.parse2dict(config, 'redis')['port']
        self.apis = PF.parse2dict(config, 'apis')
        self.users = PF.parse2dict(config, self.name)
        self.user_agent = settings['USER_AGENT']
        self.headers = Headers().headers
        self.temp = settings['TEMP_DIR']
        self.mode = mode

        try:
            os.makedirs(self.temp)
        except OSError: pass

    def start_requests(self):
        # 根据模式选择全量更新,或只更新队列
        if self.mode:
            api = self.apis['opalus_queue_list']
            companys = I.company_queue_list(api, 'tyc_status')
        else:
            api = self.apis['opalus_company_list']
            companys = I.company_list(api)

        # 登陆失败后尝试重新登陆
        def retry_login(login, cookie_file):
            retry = 0
            while not os.path.exists(cookie_file):
                try:
                    login.login()
                except Exception as e: pass
                retry += 1
                if retry >= 5: break

        login_url = 'https://www.tianyancha.com/login'
        for c in companys[:5]:
            # 验证URL是否被爬取
            RH = RedisHandle(self.host, self.port)
            search_url = 'https://www.tianyancha.com/search?key={}'.format(c['name'])
            c['link'] = search_url
            if RH.verify(self.name, search_url):
                continue

            # 登陆获取cookie
            username = random.choice(list(self.users.keys()))
            password = self.users[username]
            cookie_file = '{}/{}@{}.cookie'.format(self.temp, username, self.name)
            kwargs = {'username':username}
            kwargs['password'] = password
            kwargs['temp'] = self.temp
            kwargs['user_agent'] = self.user_agent
            kwargs['cookie_file'] = cookie_file
            kwargs['url'] = login_url
            SL = SimulatedLogin(**kwargs)
            retry_login(SL, cookie_file)

            if os.path.exists(cookie_file):
                cookies = Browser.read_cookies(cookie_file)
                self.headers['User-Agent'] = cookies[0]
                meta = {'cookiejar':True}
                meta['dont_filter'] = True
                meta['handle_httpstatus_list'] = [301, 302]
                meta['company'] = c
                yield Request(search_url, cookies=cookies[1:], headers=self.headers, meta=meta,
                              callback=self.parse_search)

    def parse_search(self, response):
        # 解析搜索页
        data = response.body.decode('utf-8', 'ignore')
        rules = eval('Rules().{}'.format(sys._getframe().f_code.co_name))

        ext = lambda data, rule: Selector(text=data).xpath(rule).extract()
        for d in ext(data, rules['block']):
            keys = list(rules['rules'].keys())
            values = [''.join(ext(d, rules['rules'][k])) for k in keys]
            rst = dict(zip(keys, values))
            if rst['name'] == response.meta['company']['name']:
                response.meta.update({'data':rst})
                yield Request(rst['url'], meta=response.meta, headers=self.headers,
                              callback=self.parse_details)
                break

    def parse_details(self, response):
        # 解析详情页
        data = response.body.decode('utf-8', 'ignore')
        rules = eval('Rules().{}'.format(sys._getframe().f_code.co_name))
        ext_fst = lambda d, r: Selector(text=d).xpath(r).extract_first()
        ext = lambda d, r: Selector(text=d).xpath(r).extract()

        item = TianyanchaItem()
        # 更新搜索页信息至爬取结果
        item.update(response.meta['data'])

        # 爬取结果中的默认字段
        item['craw_user_id'] = 5
        item['number'] = response.meta['company']['number']
        item['company'] = response.meta['company']

        # 详情页数据提取
        for pk in rules.keys():
            block = ext_fst(data, rules[pk]['block'])
            if block:
                keys = list(rules[pk]['rules'].keys())
                values = [ext(block, rules[pk]['rules'][k]) for k in keys]
                item.update(dict(zip(keys, values)))
        yield item

        # 下载字体文件(如果出现字体替换的情况下)
        #self.download_font_file(data)

    def download_font_file(data):
        # 下载字体文件
        rules = Rules.css_font
        css_url = Selector(text=data).xpath(rules['css']).extract_first()
        response = requests.get(css_url).text
        font_url = Selector(text=response).re_first(rules['font'])
        filename = '{}/{}'.format(self.temp, font_url.split(r'/')[-1])
        urlretrieve(font_url, filename)


class SimulatedLogin(object):

    def __init__(self, **kwargs):
        self.temp = kwargs['temp']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.url = kwargs['url']
        self.user_agent = kwargs['user_agent']
        self.cookie_file = kwargs['cookie_file']

    # 模拟登陆
    def capture_screenshots(self, browser):
        # Intercept verification code picture
        filename1 = '{}/fullpage1.png'.format(self.temp)
        browser.get_screenshot_as_file(filename1)
        area = browser.find_element_by_css_selector('.gt_bg.gt_show')

        left = area.location['x']
        top = area.location['y']
        right = left + area.size['width']
        bottom = top + area.size['height']

        browser.find_element_by_css_selector('.gt_slider_knob.gt_show').click()
        time.sleep(3)
        filename2 = '{}/fullpage2.png'.format(self.temp)
        browser.get_screenshot_as_file(filename2)

        picture1 = Image.open(filename1).crop((left, top, right, bottom))
        picture2 = Image.open(filename2).crop((left, top, right, bottom))
        return picture1, picture2

    def gap_offset(self, picture1, picture2, start=0, threhold=60):
        # Get the gap offset in the verification code picture
        coordinate = list()
        for x in range(start, picture1.size[0]):
            for y in range(picture1.size[1]):
                rgb1 = picture1.load()[x, y]
                rgb2 = picture2.load()[x, y]
                res1 = abs(rgb1[0] - rgb2[0])
                res2 = abs(rgb1[1] - rgb2[1])
                res3 = abs(rgb1[2] - rgb2[2])
                if not (res1 < threhold and res2 < threhold and res3 <
                        threhold):
                    coordinate.append(x)
        coordinate = list(set(coordinate))
        try:
            start = coordinate[0]
            end = [c for c in coordinate if c -
                     coordinate[coordinate.index(c) - 1] > 2][0]
            offset = end - start
        except Exception as e:
            offset = int(sum(coordinate) / len(coordinate)) 
        return offset

    def slide_tracks(self, distance):
        # Computational simulation of notch sliding trajectory
        distance += 20  # 偏移位置增加20个像素
        v, t, current = [0, 0.3, 0]
        forward_tracks = []
        middle = distance * 3 / 5
        while current < distance:
            if current < middle:
                a = 4
            else:
                a = -5
            s = v * t + (1/2) * a * (t**2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))
            t += 0.05
        back_tracks = [-4, -4, -3, -3, -2, -2, -1, -1]
        diff_value = sum(forward_tracks) - distance
        if diff_value > 0:
            back_tracks.append(-diff_value)
        return forward_tracks, sorted(back_tracks)

    def input_account_password(self, browser):
        # Waiting for loading done. click password login
        browser.find_element_by_xpath('//div[@active-tab="1"]').click()
        time.sleep(8)
        act = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[2]/input'
        pwd = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/input'
        btn = '/html/body/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[5]'
        browser.find_element_by_xpath(act).send_keys(self.username)
        browser.find_element_by_xpath(pwd).send_keys(self.password)
        browser.find_element_by_xpath(btn).click()
        time.sleep(3)
        # Waiting for loading and enter account&password
        elem = WebDriverWait(browser, 20, 0.5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'gt_popup_wrap')
            )
        )
        if not elem.is_displayed():
            browser.find_element_by_xpath(btn).click()
        time.sleep(5)

    def drag_slider(self, browser, forward_tracks, back_tracks):
        button = browser.find_element_by_css_selector('.gt_slider_knob.gt_show')
        ActionChains(browser).click_and_hold(button).perform()
        time.sleep(random.randint(5, 10) / 10)
        for ft in forward_tracks:
            ActionChains(browser).move_by_offset(xoffset=ft,
                                                 yoffset=0).perform()
        time.sleep(random.randint(8, 12) / 10)
        for bt in back_tracks:
            ActionChains(browser).move_by_offset(xoffset=bt,
                                                 yoffset=0).perform()
        time.sleep(random.randint(5, 10) / 10)
        ActionChains(browser).release(button).perform()
        time.sleep(1)

    def login(self):
        # Use browser to simulate login 'www.tianyancha.com'
        logging.getLogger('easyprocess').setLevel(logging.INFO)
        display = Display(visible=0,size=(1920,1080))
        display.start()
        firefox = Browser.firefox(self.user_agent)

        # Start simulate loging
        try:
            firefox.get(self.url)
            time.sleep(5)

            # Enter account passord and click login
            self.input_account_password(firefox)

            # Get the verification code picture and calculate the gap offset
            picture1, picture2 = self.capture_screenshots(firefox)
            offset = self.gap_offset(picture1, picture2)

            # Calculating the sliding trajectory and move slider
            forward_tracks, back_tracks = self.slide_tracks(offset)
            self.drag_slider(firefox, forward_tracks, back_tracks)
            firefox.get_screenshot_as_file('{}/login_after.png'.format(self.temp))
            time.sleep(12)

            # Store cookies after successful login
            try:
                firefox.find_element_by_css_selector('.input-group-btn.btn.-hg')
                logging.info('Simulated login success')
                cookies = firefox.get_cookies()
                cookies[0] = self.user_agent
                Browser.save_cookies(cookies, self.cookie_file)
                firefox.quit()
                display.stop()
            except Exception as e:
                logging.error(traceback.format_exc())
                firefox.quit()
                display.stop()

            firefox.quit()
            display.stop()
        except Exception as e:
            logging.error(traceback.format_exc())
            firefox.quit()
            display.stop()


class Rules(object):
    # Xpath of https://www.tianyancha.com
    #
    # 以下信息暂时未匹配规则
    # 基本信息
    #nature_label = scrapy.Field()  # 企业性质
    #advantage = scrapy.Field()  # 企业优势亮点
    #remark = scrapy.Field()  # 人工备注
    #tags = scrapy.Field()  # 标签(,分割)
    #cida_credit_rating = scrapy.Field()  # 工会认证(Integer,0=无,1=A级,2=AA级,3=AAA级)
    #is_design_center = scrapy.Field()  # 设计中心(0=否,1=省级,2=国家级)
    # 联系人信息
    #city = scrapy.Field()
    #zip_code = scrapy.Field()  # 邮编
    #contact_name = scrapy.Field()  # 联系人姓名
    #contact_phone = scrapy.Field()  # 联系人电话

    # CSS,Font
    css_font = {}
    css_font['css'] = '/html/head/link[@rel="stylesheet"]/@href'
    css_font['font'] = '.*?url\(\'(.*?\.woff)\'\).*?'

    # Search page
    parse_search = {}
    parse_search['block'] = '//div[@class="search-item sv-search-company"]'
    psr = parse_search['rules'] = {}
    psr['url'] = '//a[@tyc-event-ch="CompanySearch.Company"]/@href'
    psr['name'] = '//a[@tyc-event-ch="CompanySearch.Company"]//text()'
    psr['company_status_label'] = '//div[@class="tag num-opening"]/text()'
    psr['founder'] = '//a[@class="legalPersonName link-click"]/text()'
    psr['province'] = '//span[@class="site"]/text()'
    psr['registered_capital'] = '//div[@class="title  text-ellipsis"][1]/span/text()'
    psr['registered_time'] = '//div[@class="title  text-ellipsis"][2]/span/text()'
    psr['ty_score'] = '//span[@class="score-num"]/text()'

    # Details page
    parse_details = {}
    # 公司基础简介块
    pdb = parse_details['basic'] = {}
    pdb['block'] = '//div[@class="box -company-box "]'
    pdbr = pdb['rules'] = {}
    pdbr['logo_url'] = '//div[@class="logo -w100"]/img/@data-src'
    pdbr['url'] = '//a[@tyc-event-ch="CompangyDetail.Head.website"]/text()'
    pdbr['tel'] = '//div[@class="detail "]//div[@class="f0"][1]//div[1]//span//text()'
    pdbr['contact_email'] = '//div[@class="detail "]//div[@class="f0"][1]//div[2]//span//text()'
    pdbr['address'] = '//div[@class="detail "]//div[@class="f0"][2]//div[2]//text()'
    pdbr['description'] = '//script[@id="company_base_info_detail"]/text()'
    pdbr['ty_view_count'] = '//span[@class="pv-txt"]/text()'
    pdbr['is_high_tech'] = '//span[@class="tag tag-new-category mr10"]/text()'
    pdbr['short_name'] = '//div[@class="content-top"]/span[@class=""]/text()'

    # 更新时间块
    pdut = parse_details['update_time'] = {}
    pdut['block'] = '//div[@class="footer"]'
    pdutr = pdut['rules'] = {}
    pdutr['ty_last_time'] = '//span[@class="updatetimeComBox"]/text()'

    # 天眼风险块
    pdtr = parse_details['tyc_risk'] = {}
    pdtr['block'] = '//div[@class="company-panel-warp -panel-content"]'
    pdtrr = pdtr['rules'] = {}

    # 公司背景块列表
    pdcp = parse_details['company_profile'] = {}
    pdcp['block'] = '//div[@class="item-container"][1]'
    pdcpr = pdcp['rules'] = {}
    pdcpr['key_personnel_count'] = '//div[@class="itemcontent   "]//div[5]/span/text()'
    pdcpr['shareholder_count'] = '//div[@class="itemcontent   "]//div[6]/span/text()'
    pdcpr['investment_abroad_count'] = '//div[@class="itemcontent   "]//div[8]/span/text()'
    pdcpr['annual_return_count'] = '//div[@class="itemcontent   "]//div[16]/span/text()'
    pdcpr['chage_record_count'] = '//div[@class="itemcontent   "]//div[14]/span/text()'
    pdcpr['affiliated_agency_count'] = '//div[@class="itemcontent   "]//div[17]/span/text()'

    # 司法风险块
    pdjr = parse_details['judicial_risk'] = {}
    pdjr['block'] = '//div[@class="item-container"][2]'
    pdjrr = pdjr['rules'] = {}
    pdjrr['action_at_law_count'] = '//div[@class="itemcontent -no-border "]//div[3]/span/text()'
    pdjrr['court_announcement_count'] = '//div[@class="itemcontent -no-border "]//div[5]/span/text()'
    pdjrr['dishonest_person_count'] = '//div[@class="itemcontent -no-border "]//div[7]/span/text()'
    pdjrr['person_subject_count'] = '//div[@class="itemcontent -no-border "]//div[9]/span/text()'
    pdjrr['announcement_court_count'] = '//div[@class="itemcontent -no-border "]//div[1]/span/text()'

    # 经营风险块
    pdbr = parse_details['business_risk'] = {}
    pdbr['block'] = '//div[@class="item-container"][3]'
    pdbrr = pdbr['rules'] = {}
    pdbrr['abnormal_operation_count'] = '//div[@class="itemcontent -no-border "]//div[1]/span/text()'
    pdbrr['administrative_penalty_count'] = '//div[@class="itemcontent -no-border "]//div[2]/span/text()'
    pdbrr['break_law_count'] = '//div[@class="itemcontent -no-border "]//div[4]/span/text()'
    pdbrr['equity_pledged_count'] = '//div[@class="itemcontent -no-border "]//div[5]/span/text()'
    pdbrr['chattel_mortgage_count'] = '//div[@class="itemcontent -no-border "]//div[7]/span/text()'
    pdbrr['tax_notice_count'] = '//div[@class="itemcontent -no-border "]//div[9]/span/text()'
    pdbrr['judicial_sale_count'] = '//div[@class="itemcontent -no-border "]//div[10]/span/text()'

    # 公司发展块
    pdcd = parse_details['company_develop'] = {}
    pdcd['block'] = '//div[@class="item-container"][4]'
    pdcdr = pdcd['rules'] = {}
    pdcdr['financing_count'] = '//div[@class="itemcontent -no-border "]//div[1]/span/text()'
    pdcdr['core_team_count'] = '//div[@class="itemcontent -no-border "]//div[2]/span/text()'
    pdcdr['enterprise_business_count'] = '//div[@class="itemcontent -no-border "]//div[3]/span/text()'
    pdcdr['investment_events_count'] = '//div[@class="itemcontent -no-border "]//div[4]/span/text()'
    pdcdr['competitor_count'] = '//div[@class="itemcontent -no-border "]//div[5]/span/text()'

    # 经营状况块
    pdbs = parse_details['business_state'] = {}
    pdbs['block'] = '//div[@class="item-container"][5]'
    pdbsr = pdbs['rules'] = {}
    pdbsr['bid_count'] = '//div[@class="itemcontent -no-border "]//div[7]/span/text()'
    pdbsr['tax_rating_count'] = '//div[@class="itemcontent -no-border "]//div[4]/span/text()'
    pdbsr['product_count'] = '//div[@class="itemcontent -no-border "]//div[8]/span/text()'
    pdbsr['import_and_export_credit_count'] = '//div[@class="itemcontent -no-border "]//div[10]/span/text()'
    pdbsr['certification_count'] = '//div[@class="itemcontent -no-border "]//div[6]/span/text()'
    pdbsr['wx_public_count'] = '//div[@class="itemcontent -no-border "]//div[9]/span/text()'

    # 知识产权块
    pdkp = parse_details['knowledge_property'] = {}
    pdkp['block'] = '//div[@class="item-container"][6]'
    pdkpr = pdkp['rules'] = {}
    pdkpr['trademark_count'] = '//div[@class="itemcontent -no-border "]//div[1]/span/text()'
    pdkpr['patent_count'] = '//div[@class="itemcontent -no-border "]//div[2]/span/text()'
    pdkpr['software_copyright_count'] = '//div[@class="itemcontent -no-border "]//div[3]/span/text()'
    pdkpr['works_copyright_count'] = '//div[@class="itemcontent -no-border "]//div[4]/span/text()'
    pdkpr['icp_count'] = '//div[@class="itemcontent -no-border "]//div[5]/span/text()'

    # 历史信息块
    pdhi = parse_details['history_info'] = {}
    pdhi['block'] = '//div[@class="item-container"][7]'
    pdhir = pdhi['rules'] = {}

    # 工商信息块
    pdbi = parse_details['business_info'] = {}
    pdbi['block'] = '//div[@id="_container_baseInfo"]'
    pdbir = pdbi['rules'] = {}
    pdbir['founder'] = '//div[@class="name"]/a/text()'
    pdbir['founder_desc'] = '//div[@class="name"]/a/@href'
    pdbir['registered_capital'] = '//table[@class="table -striped-col -border-top-none"]//tr[1]//td[2]/div/text()'
    pdbir['registered_time'] = '//table[@class="table -striped-col -border-top-none"]//tr[1]//td[4]/div/text()'
    pdbir['company_count'] = '//div[@class="company"]/span/text()'
    pdbir['company_type'] = '//table[@class="table -striped-col -border-top-none"]//tr[4]//td[4]/text()'
    pdbir['registration_number'] = '//table[@class="table -striped-col -border-top-none"]//tr[2]//td[4]/text()'
    pdbir['credit_code'] = '//table[@class="table -striped-col -border-top-none"]//tr[3]//td[2]/text()'
    pdbir['identification_number'] = '//table[@class="table -striped-col -border-top-none"]//tr[4]//td[2]/text()'
    pdbir['industry'] = '//table[@class="table -striped-col -border-top-none"]//tr[5]//td[4]/text()'
    pdbir['business_term'] = '//table[@class="table -striped-col -border-top-none"]//tr[5]//td[2]/span/text()'
    pdbir['issue_date'] = '//table[@class="table -striped-col -border-top-none"]//tr[6]//td[4]/text()'
    pdbir['registration_authority'] = '//table[@class="table -striped-col -border-top-none"]//tr[8]//td[4]/text()'
    pdbir['english_name'] = '//table[@class="table -striped-col -border-top-none"]//tr[9]//td[4]/text()'
    pdbir['registered_address'] = '//table[@class="table -striped-col -border-top-none"]//tr[9]//td[2]/text()'
    pdbir['scope_business'] = '//span[@class="js-full-container hidden"]/text()'
    pdbir['organization_code'] = '//table[@class="table -striped-col -border-top-none"]//tr[3]//td[4]/text()'
    pdbir['scale_label'] = '//table[@class="table -striped-col -border-top-none"]//tr[7]//td[4]/text()'

    # 微信公众号块
    pdwn = parse_details['weichat_num'] = {}
    pdwn['block'] = '//div[@tyc-event-ch="CompangyDetail.wechat"]'
    pdwnr = pdwn['rules'] = {}
    pdwnr['wx_public'] = '//div[@class="title"]/text()'
    pdwnr['wx_public_no'] = '//div[@class="content"]//div[2]//span[2]/text()'
    pdwnr['wx_public_qr'] = '//div[@class="erweima-pic"]/img/@data-src'
