# -*- coding: utf-8 -*-

# Scrapy settings for thepaper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import datetime
BOT_NAME = 'thepaper'

SPIDER_MODULES = ['thepaper.spiders']
NEWSPIDER_MODULE = 'thepaper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'thepaper (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'thepaper.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'thepaper.middlewares.MyCustomDownloaderMiddleware': 543,
#}
DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
        'thepaper.rotate_useragent.ProxyMiddleware' : None, #代理
        'thepaper.rotate_useragent.RotateUserAgentMiddleware' :400, #User_agent
    }
# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'thepaper.pipelines.selectKeywordPipeline': 300,
   'thepaper.pipelines.MongoPipeline': 301,

}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'


USER_AGENT_LIST=[\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]
PROXIES=[
    {'ip_port': '111.11.228.75:80', 'user_pass': ''},
    {'ip_port': '120.198.243.22:80', 'user_pass': ''},
    {'ip_port': '111.8.60.9:8123', 'user_pass': ''},
    {'ip_port': '101.71.27.120:80', 'user_pass': ''},
    {'ip_port': '122.96.59.104:80', 'user_pass': ''},
    {'ip_port': '122.224.249.122:8088', 'user_pass': ''},
]

END_DAY = 1
#爬取新闻的×天前的相对时间，默认当天凌晨。也就是爬取当天凌晨的×天前的新闻
END_NOW = datetime.datetime.combine(datetime.date.today(), datetime.time.min) #当天0点
# END_NOW = datetime.datetime.now() #当时
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #现在时间的格式

#MongoDB URI
MONGO_URI = 'mongodb://localhost:27017/'

#MongoDB databases
MONGO_DATABASE = 'News'

HTTPERROR_ALLOWED_CODES= [521]

#spider's name 和网站的对应关系
SPIDER_NAME = {
    "carnoc": "民航资源网",
    "caacnews": "中国民航报",
    "mhyw": "中国民用航空网",
    "cntour2": "中国旅游新闻网",
    "toptour": "第一旅游网",
    "cnta":"国家旅游局",
    "tech_ifeng":"凤凰科技",
    "techqq": "腾讯科技",
    "tech163": "网易科技",
    "tmtpost": "钛媒体",
    "iheima":"i黑马",
    "36kr": "36氪",
    "donews": "Donews",
    "techweb": "Techweb",
    "thepaper": "澎湃新闻",
    "jiemian": "界面新闻",
    "wshang": "天下网商",
    "nbd": "每日经济",
    "yicai": "一财网",
    "money163": "网易财经",
    "cyzone": "创业邦",
    "leiphone": "雷锋网",
    "cb": "中国经营报",
    "luxe": "华丽志",
    "wallstreetcn": "华尔街见闻",
    "qdaily": "好奇心日报",
    "twc": "Travel weekly China",
    "meadin": "迈点网",
    "ctcnn": "劲旅网",
    "wechat": "微信公众号",
    "baidunews": "百度新闻"
}

WECHAT_IDS = [
    "caacnews-official",
    "liwuli_hotels",
    "travelskygds",
    "ThingsOfAirlines",
    "icarnoc",
    "bvmagazine",
    "wow36kr",
    "huxiu_com",
    "guifabucom",
    "pinchain",
    "wepingwest",
    "GP4008202018",
    "ctcnn1",
    "dotours",
    "meadin1",
    "thepapernews",
    "qqtech",
    "zglybs",
    "lvjienews",
    "ph1240888257",
    "B1-12F",
    "BBTtravel",
    "LuxeCO",
    "otadaily",
    "ehotelier",
]

WECHAT_NAME = {
    "caacnews-officials": "中国民航网",
}

LOG_LEVEL = "INFO"

LOG_FORMATTER = 'thepaper.polite_log_formatter.PoliteLogFormatter'
