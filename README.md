基于[Scrapy](https://scrapy.org/ "scrapy官网")框架的网络爬虫系统
===


### 环境配置

Python虚拟环境配置
```Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

CentOS7+系统浏览器配置
```Bash
# Firefox
yum install xorg-x11-server-Xvfb bzip gtk3 -y
wget https://download-ssl.firefox.com.cn/releases/firefox/66.0/en-US/Firefox-latest-x86_64.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -jxvf Firefox-latest-x86_64.tar.bz2 -C /opt/software/
tar -zxvf geckodriver-v0.24.0-linux64.tar.gz -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/firefox.sh
echo "export PATH=\$PATH:/opt/software/firefox" >> /etc/profile.d/firefox.sh
```

```Bash
# PhantomJS
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar -jxvf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /opt/software/
echo "#!/bin/bash" > /etc/profile.d/phantomjs.sh
echo "export PATH=\$PATH:/opt/software/phantomjs-2.1.1-linux-x86_64/bin" >> /etc/profile.d/phantomjs.sh
```

Ubuntu18.04_+系统浏览器配置
```Bash
# Firefox
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

```Bash
# Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
wget http://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip
apt-get install xvfb libxi6 libgconf-2-4 -y
apt-get install -f
dpkg -i google-chrome-stable_current_amd64.deb
unzip chromedriver_linux64.zip -d /usr/bin/
```


### BUG问题
Ubuntu18.04 firefox截图乱码
```Bash
apt-get install fonts-arphic-uming -y
```
