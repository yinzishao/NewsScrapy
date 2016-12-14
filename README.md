# NewsScrapy
基于scrapy、selenium、beautifulsoup、pyvirtualdisplay的新闻爬虫

###问题：

####一财网：js生成cookie，无法直接访问，使用selenium解决；

####中国经营报：直接访问会报521错误，js生成cookie后重定向才能得到首页，phantomjs并不能解决这个重定向,但Firefox可以解决。

####为了不让浏览器打开，用了headless-firefox。具体教程参考：http://scraping.pro/use-headless-firefox-scraping-linux/		**使用selenium和scrapy结合代码可看yicai_spider.py**

包括列表有：

网站名称	网站链接  
民航资源网	http://news.carnoc.com/  	
中国民航报	http://www.caacnews.com.cn/  	
中国民用航空网	http://www.caac.gov.cn/XWZX/MHYW/  	
网易财经	http://money.163.com/special/002526O5/transport.html  	
中国旅游新闻网	http://www.cntour2.com/  	
中国旅游报	http://www.toptour.cn/home/  	
第一旅游网	http://www.toptour.cn/home/  	
国家旅游局	http://www.cnta.gov.cn/xxfb/  	
凤凰科技	http://www.donews.com/  	
腾讯科技	http://www.iheima.com/	
网易科技	http://tech.ifeng.com/  	
钛媒体	http://tech.qq.com/  	
虎嗅	http://tech.163.com/internet  	
i黑马	http://www.tmtpost.com/  	
36氪	http://www.huxiu.com/  	
Donews	http://www.36kr.com/  	
Techweb	http://www.techweb.com.cn/news/  	
澎湃新闻	http://www.thepaper.cn/	  
界面新闻	http://www.jiemian.com/  	
天下网商	http://i.wshang.com/  	
每日经济	http://www.nbd.com.cn/  	
21世纪	http://www.21cbh.com/  	
一财网	http://www.yicai.com/  	
网易财经	http://money.163.com/special/002526O5/transport.html  	
创业邦	http://www.cyzone.cn/  	
雷锋网	http://www.leiphone.com/  	
中国经营报	http://www.cb.com.cn/  	
华丽志	http://luxe.co/  	
华尔街见闻	http://wallstreetcn.com/  	
好奇心日报	http://www.qdaily.com/  	
Travel weekly China	http://www.travelweekly-china.com/  	
迈点网	http://www.meadin.com/  	
劲旅网	http://www.ctcnn.com/  	
品橙旅游	http://www.pinchain.com/  	
		
公众号	帐号	
中国民航网	caacnews-officials	
里屋里酒店咨讯	liwuli-hotels	
航旅同行	travelskygds	
航企哪些事儿	ThingsOfAirlines	
航旅IT圈子	icarnoc	
民航资源网	bvnagzine	
商业价值	wow36kr	
36氪	huxiu-com	
虎嗅网	guifabucom	
硅发布	pinchain	
品橙旅游	wepingwest	
pingwest中文网	GP4008202018	
智慧旅行	ctcnn1	
劲旅网	dotours	
旅游圈	meadin1	
迈点网	thepapernews	
澎湃新闻	qqtech	
腾讯科技	zglybs	
旅界	lvjienews	
旅游商业观察	ph1240888257	
B座12楼	B1-12F	
BBTtravel	BBTtravel	
华丽志	LuxeCO	
在线旅讯	otadaily	
酒店内参	ehotelier	
星硕袁学娅专栏		

