# -*- coding: utf-8 -*-
#
# Accessing Website with Browsers
import re
import os
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Browser(object):

    @staticmethod
    def phantomjs(user_agent, load_image=False):
        # PhantomJS browser simulation
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap['phantomjs.page.settings.userAgent'] = (user_agent)
        dcap['phantomjs.page.settings.loadImages'] = load_image
        dcap['phantomjs.page.settings.disk-cache'] = True
        dcap['phantomjs.page.settings.ignore-ssl-errors'] = True
        exec_path = re.sub(r'\n', '', os.popen('which phantomjs').read())
        phantomjs = webdriver.PhantomJS(executable_path=exec_path,
                                        service_log_path='/dev/null',
                                        desired_capabilities=dcap)
        phantomjs.implicitly_wait(60)
        phantomjs.set_page_load_timeout(60)
        phantomjs.maximize_window()
        return phantomjs

    @staticmethod
    def firefox(user_agent):
        # Firefox browser simulation
        args = ['--ignore-ssl-errors=true']
        exec_path = re.sub(r'\n', '', os.popen('which geckodriver').read())
        firefox = webdriver.Firefox(executable_path=exec_path,
                                    log_path='/dev/null')
        firefox.implicitly_wait(60)
        firefox.set_page_load_timeout(60)
        firefox.maximize_window()
        firefox.desired_capabilities.update({'user_agent':user_agent})
        return firefox

    @staticmethod
    def chrome(user_agent):
        # Chrome browser simulation
        options=webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent={}'.format(user_agent))
        exec_path = re.sub(r'\n', '', os.popen('which chromedriver').read())
        chrome=webdriver.Chrome(executable_path=exec_path, chrome_options=options)
        chrome.implicitly_wait(60)
        chrome.set_page_load_timeout(60)
        return chrome

    @staticmethod
    def save_cookies(cookies, filename):
        fw = open(filename, 'w')
        fw.write(json.dumps(cookies))
        fw.close()

    @staticmethod
    def read_cookies(filename):
        fr = open(filename, 'r')
        cookies = json.loads(fr.read())
        fr.close()
        return cookies


if __name__ == '__main__':
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0'

    # Test phantomjs
    phantomjs = Browser.phantomjs(ua)
    url = 'https://www.sogou.com/'
    phantomjs.get(url)
    print(phantomjs.title)
    phantomjs.quit()

    # Test firefox
    from pyvirtualdisplay import Display
    import logging
    logging.getLogger('easyprocess').setLevel(logging.INFO)
    display = Display(visible=0,size=(1920,1080))
    display.start()
    firefox = Browser.firefox(ua)
    url = 'https://www.baidu.com/'
    firefox.get(url)
    print(firefox.title)
    firefox.quit()
    display.stop()

    # Test chrome
    chrome = Browser.chrome(ua)
    url = 'https://cn.bing.com/'
    chrome.get(url)
    print(chrome.title)
    chrome.quit()
