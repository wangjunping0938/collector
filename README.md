基于[Scrapy](https://scrapy.org/ "scrapy官网")框架的网络爬虫系统
===


### 项目部署说明

- [环境配置](#环境配置)
- [项目部署](#项目部署)
- [项目管理](#项目管理)
- [Linux系统定时任务](#Linux系统定时任务)


#### 环境配置
---
**Python虚拟环境配置**
```Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

###### CentOS7+系统浏览器配置
- Firefox
```Bash
yum install xorg-x11-server-Xvfb bzip gtk3 -y
wget https://download-ssl.firefox.com.cn/releases/firefox/66.0/en-US/Firefox-latest-x86_64.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -jxvf Firefox-latest-x86_64.tar.bz2 -C /opt/software/
tar -zxvf geckodriver-v0.24.0-linux64.tar.gz -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/firefox.sh
echo "export PATH=\$PATH:/opt/software/firefox" >> /etc/profile.d/firefox.sh
```
- PhantomJS
```Bash
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar -jxvf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/phantomjs.sh
echo "export PATH=\$PATH:/opt/software/phantomjs-2.1.1-linux-x86_64/bin" >> /etc/profile.d/phantomjs.sh
```

**Ubuntu18.04+系统浏览器配置**
- Firefox
```Bash
apt-get install libgtk-3-dev -y
apt-get install xvfb -y
apt-get install libdbus-glib-1-2 -y
wget https://download-ssl.firefox.com.cn/releases/firefox/66.0/en-US/Firefox-latest-x86_64.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -jxvf Firefox-latest-x86_64.tar.bz2 -C /opt/software/
tar -zxvf geckodriver-v0.24.0-linux64.tar.gz -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/firefox.sh
echo "export PATH=\$PATH:/opt/software/firefox" >> /etc/profile.d/firefox.sh
```
- Chrome
```Bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
wget http://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip
apt-get install xvfb libxi6 libgconf-2-4 -y
apt-get install -f
dpkg -i google-chrome-stable_current_amd64.deb
unzip chromedriver_linux64.zip -d /usr/bin/
```

**Ubuntu18.04+Redis数据库配置**
```Bash
apt-get install tcl tcl-dev -y
apt-get install redis-server -y
service redis-server start
```


项目部署
------
**启动爬虫项目部署**
- 启动管理服务
```Bash
sh deployment/scrapyd-service.sh start
```
- 部署爬虫项目至管理工具
```Bash
sh deployment/deploy.sh
```

项目管理
------
**爬虫管理相关指令**
```Bash
# 检查爬虫负载信息
curl http://localhost:6800/daemonstatus.json

# 启动爬虫文件(project=项目名称, spider=爬虫名称, mode=启动爬虫参数)
curl http://localhost:6800/schedule.json -d project=collector -d spider=tianyancha -d mode=update

# 查看当前爬虫版本信息
curl http://localhost:6800/listversions.json?project=collector

# 终止爬虫进程
curl http://localhost:6800/cancel.json -d project=collector -d job=ae8c423cd05411e88449000c29deb11c

# 查看爬虫项目列表信息
curl http://localhost:6800/listprojects.json

# 查看爬虫项目中爬虫文件列表
curl http://localhost:6800/listspiders.json?project=collector

# 查看当前已完成爬虫的信息
curl http://localhost:6800/listjobs.json?project=collector|python -m json.tool

# 将爬虫项目从管理工具移除
curl http://localhost:6800/delversion.json -d project=collector -d version=1539591444
curl http://localhost:6800/delversion.json -d project=collector
```

Linux系统定时任务
------
**编辑`/etc/crontab`**
```Bash
0 11 * * * root curl http://127.0.0.1:6800/schedule.json -d project=collector -d spider=tianyancha -d mode=update
```


BUG问题
------
**Ubuntu18.04 firefox截图乱码**
```Bash
apt-get install fonts-arphic-uming -y
```
