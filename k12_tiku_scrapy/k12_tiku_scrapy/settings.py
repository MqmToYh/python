# -*- coding: utf-8 -*-

# Scrapy settings for k12_tiku_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'k12_tiku_scrapy'

SPIDER_MODULES = ['k12_tiku_scrapy.spiders']
NEWSPIDER_MODULE = 'k12_tiku_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'k12_tiku_scrapy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# 配置并发
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#禁止使用cookies
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'k12_tiku_scrapy.middlewares.K12TikuScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'k12_tiku_scrapy.middlewares.MyCustomDownloaderMiddleware': 543,
    #'k12_tiku_scrapy.middlewares.ProxyMiddleware': 100,
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 150,
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware':50,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'k12_tiku_scrapy.pipelines.K12TikuScrapyPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#线程池的大小
REACTOR_THREADPOOL_MAXSIZE  =  50
#禁用重试
RETRY_ENABLED = False
#logger配置 LOG_FILE  LOG_ENABLED LOG_ENCODING LOG_LEVEL  LOG_FORMAT  LOG_DATEFORMAT  LOG_STDOUT
LOG_LEVEL = 'INFO' #INFO、WARN、ERROR
LOG_FILE = 'log.txt'

#文件保存的根路径 必须加“/”结尾
root_path = 'data/'
#图片保存路径 必须加“/”结尾
pic_path = 'data/pic/'
#未下载文件后缀 
tmp_suffix = '-tmp'
#开始爬取的学科
start_urls = [
    #'testPaper.html?hdSearch=&key=&sct=1&cn=数学&st=0&cid=500014',
    #'testPaper.html?hdSearch=&key=&sct=1&cn=数学&st=1&cid=500010',
    #'testPaper.html?hdSearch=&key=&sct=1&cn=数学&st=2&cid=500004',
    #'testPaper.html?hdSearch=&key=&sct=1&cn=地理&st=1&cid=500005'
    #'testPaper.html?hdSearch=&key=&sct=1&cn=地理&st=2&cid=500009',
    'testPaper.html?hdSearch=&key=&sct=1&cn=思品&st=1&cid=500006',
    #'testPaper.html?hdSearch=&key=&sct=1&cn=政治&st=2&cid=500008',
]
