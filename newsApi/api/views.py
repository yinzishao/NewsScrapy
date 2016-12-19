#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import pymongo
from django.conf import settings
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_jsonp.renderers import JSONPRenderer
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE]
newsCol = db['news']    #新闻集合
wechatCol = db['wechat'] #微信公众号集合

@api_view(['GET'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def index(request):
    """
    首页
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = newsCol.find_one({})
        return Response(data)


@api_view(['GET', 'POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getSource(request):
    """
    获取新闻来源列表
    :param request:
        {
            "start": 0,
            "size": 6
        }
    :return:
        [
            {
                "count": number,
                "_id": string
            }
        ]
    """
    pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
    data = newsCol.aggregate(pipeline)
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))
    elif request.method == 'POST':
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size
    resultList = list(data)[start : start + size]
    return Response(resultList)

@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getCatalogue(request):
    """
    获取某个新闻网站的类别列表
    :param request:
        {
            "source": "澎湃新闻"
        }
    :return:

    """
    if request.method == 'GET':
        source = request.GET.get('source', None)
    if request.method == 'POST':
        source = request.data.get('source', None)
    pipeline = [{
        "$match":{
            'source': source
        }
    },{
        "$group": {
            "_id": "$catalogue",
            "count": {"$sum": 1}
        }
    }]
    data = newsCol.aggregate(pipeline)
    return Response(list(data))


@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getNewsList(request):
    """
    根据新闻来源和新闻分类返回相对应的新闻列表
    :param request:
        {
            "start": 0,
            "size": 6,
            "source": "澎湃新闻",
            "catalogue": "精选内容"
        }
    :return:
        news items list
    """
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))
        source = request.GET.get('source', None)
        catalogue = request.GET.get('catalogue', None)
    if request.method == 'POST':
        source = request.data.get('source', None)
        catalogue = request.data.get('catalogue', None)
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size
    #获取新闻的简要信息
    data = newsCol.find({"source": source, "catalogue": catalogue}).skip(start).limit(size)
    resultList = list(data)
    return Response(resultList)

@api_view(['GET'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getNews(request, id):
    """
    根据id获取新闻
    :param request:
    :return: News Item

    """
    news = newsCol.find_one({'_id': id})
    return Response(news)

@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getKeywords(request):
    """
    获取关键词
    :param request:
        {
            "start":0,
            "size":6
        }
    :return:
        [
            {
                "count": 1,
                "_id": "星级酒店"
            },
        ]
    """
    size = 6
    start = 0
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))

    if request.method == 'POST':
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size

    pipeline = [{
        "$project": {"keywords": 1, "title": 1}

    },{
        "$unwind": "$keywords",
    },{
        "$group": {"_id": "$keywords", "count": {"$sum": 1}}
    }]
    resultList = list(newsCol.aggregate(pipeline))
    return Response(resultList[start: start + size])



@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getNewsByKey(request):
    """
    根据传过去的关键词id返回该关键词下的新闻列表
    :param request:
        {
            "_id": "国航",
            "start": 0,
            "size": 6
        }
    :return:
    """
    size = 6
    start = 0
    keyword = ""
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))
        keyword = request.GET.get('_id', 0)
    if request.method == 'POST':
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size
        keyword = request.data.get('_id', "")
    resultList = list(newsCol.find({"keywords": keyword}))
    return Response(resultList[start : start + size])


@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getWechatSource(request):
    """
    获取公众号来源列表
    :param request:
        {
            "start": 0,
            "size": 6
        }
    :return:
        [
            {
                "count": number,
                "_id": string
            }
        ]
    """
    pipeline = [{"$group": {"_id": "$weixin_name", "count": {"$sum": 1}}}]
    data = wechatCol.aggregate(pipeline)
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))

    if request.method == 'POST':
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size

    resultList = list(data)[start : start + size]
    return Response(resultList)

@api_view(['GET','POST'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getWechatList(request):
    """
    获取某个公众号的文章列表
    :param request:
        {
            "start": 0,
            "size": 6,
            "weixin_name": "虎嗅网"
        }
    :return:
        wechat items list
    """
    if request.method == 'GET':
        size = int(request.GET.get('size', 6))
        start = int(request.GET.get('start', 0))
        weixin_name = request.GET.get('weixin_name')

    if request.method == 'POST':
        size = int(request.data.get('size', 6))
        start = int(request.data.get('start', 0)) * size
        weixin_name = request.data.get('weixin_name')
    data = wechatCol.find({'weixin_name' : weixin_name}).skip(start).limit(size)
    return Response(list(data))

@api_view(['GET'])
@renderer_classes((BrowsableAPIRenderer, JSONRenderer,JSONPRenderer))
def getWechat(request, id):
    """
    根据公众号id获取公众号的文章
    :param request:
    :return:
    """
    data = wechatCol.find_one({"_id": id})
    return Response(data)

class News(APIView):
    def get(self, request, format = None):
        data = db['news'].find_one({})
        return Response(data)

