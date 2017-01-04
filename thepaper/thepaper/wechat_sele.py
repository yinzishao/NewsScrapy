# -*- coding: utf-8 -*-
__author__ = 'k'

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import pymongo
import random
from util import judge_news_crawl,judge_key_words
from bson.objectid import ObjectId
from pyvirtualdisplay import Display
from selenium import webdriver
from settings import MONGO_URI,MONGO_DATABASE,WECHAT_IDS
from bs4 import BeautifulSoup
# display = Display(visible=0, size=(800, 600))
# display.start()
chromedriver = "/home/youmi/Downloads/chromedriver"
driver = webdriver.Chrome(chromedriver)
def search_public(weixin_id):
    '''
        搜索公众号
    :param weixinhao: 公众号 如 icarnoc
    :return:
    '''
    driver.get("http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=y&_sug_type_=" % weixin_id)
    time.sleep(random.randint(5,15))
    code = driver.page_source
    # r = s.get("http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=y&_sug_type_=" % weixin_id) # 公众号名称提交查询
    soup = BeautifulSoup(code,"lxml")
    url = soup.find("a",uigs="main_toweixin_account_image_0").get("href")   #获得公众号的主页
    name =  soup.find("a",uigs="main_toweixin_account_name_0").text.strip()
    return url,name

def get_article_list(home_url,weixin_id,weixin_name):
    '''
        获取公众号的文章列表
    :param url: 公众号主页
    :return:
    '''
    print home_url
    # driver = webdriver.Chrome(chromedriver)
    # driver.get(home_url)
    script_url = "window.open('" + home_url +"', 'new_window')"
    driver.execute_script(script_url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(random.randint(5,15))
    code = driver.page_source
    # driver.quit()
    msg = re.search(r"var msgList =([\W\w]+?)seajs.use",code).group(1).strip()[:-1]  # 获得公众号的文章列表
    msg_dict = json.loads(msg)
    article_list = []
    for u in msg_dict["list"]:
        news_date = u["comm_msg_info"]["datetime"]  #某天所有发布的文章的时间戳
        news_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(news_date)))  #时间转换
        title = u["app_msg_ext_info"]["title"] #某天最后跟新的文章的标题
        news_url = "http://mp.weixin.qq.com" + u["app_msg_ext_info"]["content_url"] #某天最后跟新的文章的url
        pic = u["app_msg_ext_info"]["cover"]    #某天最后跟新的文章的图片
        abstract = u["app_msg_ext_info"]["digest"] #某天最后跟新的文章的摘要
        author = u["app_msg_ext_info"]["author"] # 某天最后跟新的文章的作者
        fileid = u["app_msg_ext_info"]["fileid"] # 某天最后跟新的文章的fileid
        source_url = u["app_msg_ext_info"]["source_url"] # 某天最后跟新的文章的来源信息
        article = {
            "weixin_id":weixin_id,
            "weixin_name":weixin_name,
            "news_date":news_date,
            "title":title,
            "news_url":news_url.replace("&amp;","&").replace("&amp;","&"),
            "pic":pic,
            "abstract":abstract,
            "author":author,
            "fileid":fileid,
            "source_url":source_url,
            "crawl_date":time.strftime('%Y-%m-%d %H:%M:%S')
       }
        article = judge_news_crawl(article)
        if article:
            article_list.append(article)
        for c in u["app_msg_ext_info"]["multi_app_msg_item_list"]:
            title = c["title"] #某天的文章的标题
            news_url = "http://mp.weixin.qq.com" + c["content_url"] #某天的文章的url
            pic = c["cover"]    #某天的文章的图片
            abstract = c["digest"] #某天的文章的摘要
            author = c["author"] # 某天的文章的作者
            fileid = c["fileid"] # 某天的文章的fileid
            source_url = c["source_url"] # 某天的文章的来源url
            article = {
                "weixin_id":weixin_id,
                "weixin_name":weixin_name,
                "news_date":news_date,
                "title":title,
                "news_url":news_url.replace("&amp;","&").replace("&amp;","&"),
                "pic":pic,
                "abstract":abstract,
                "author":author,
                "fileid":fileid,
                "source_url":source_url,
                "crawl_date":time.strftime('%Y-%m-%d %H:%M:%S')
            }
            article = judge_news_crawl(article)
            if article:
                article_list.append(article)
    return article_list


def article_content(article_list):
    '''
        获取每个文章的内容
    :param article_list: 公众号文章列表
    :return:
    '''
    result = []
    for c in article_list:
        # driver = webdriver.Chrome(chromedriver)
        print c["news_url"]
        script_url = "window.open('" + c["news_url"] +"', 'new_window')"
        # print script_url
        # driver.get(c["news_url"])
        driver.execute_script(script_url)
        time.sleep(random.randint(5,15))
        driver.switch_to.window(driver.window_handles[-1])
        code = driver.page_source
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        soup = BeautifulSoup(code,"lxml")
        c["content"] = soup.find_all('div',class_ = 'rich_media_content')[0].text.strip() if soup.find_all('div',class_ = 'rich_media_content')[0] else None
        item_keywords = judge_key_words(c)
        if item_keywords:   #筛选出有关键词的item
            c["keywords"] = item_keywords
            print "存在关键词"
            result.append(c)
        else:
            print c["news_url"]
            print "不存在关键词"
    return result

def insertMongoDB(items):
    collection_name = 'wechat'
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    for item in items:
        item['_id'] = str(ObjectId())
        db[collection_name].insert(dict(item))


if __name__ == "__main__":
    with open('wechat.json', 'r') as f :
        data = f.read()
        d = json.loads(data)
        index = d["index"]
        if index < 24:
            d["index"]=d["index"]+1
        else:
            d["index"]=0
    with open('wechat.json', 'w') as f :
        f.write(json.dumps(d))
    print "crawl the index of wechat:"
    print index
    s = requests.Session()
    weixin_id = WECHAT_IDS[index]
    home_url,weixin_name = search_public(weixin_id)
    article_list = get_article_list(home_url,weixin_id,weixin_name)
    # print article_list
    print len(article_list)
    result = article_content(article_list)
    # print result
    insertMongoDB(result)
    # display.stop()
    driver.quit()