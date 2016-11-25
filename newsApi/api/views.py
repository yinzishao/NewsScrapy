#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import pymongo
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from bson.objectid import ObjectId

client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DATABASE]
newsCol = db['news']    #新闻集合

##TODO:修改_id类型

@api_view(['GET'])
def index(request):
    """
    首页
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = newsCol.find_one({},{'_id':0})
        # data['_id'] = data['_id'].toString()
        # print data
        return Response(data)
        return HttpResponse(u"欢迎光临 自强学堂!")


@api_view(['GET', 'POST'])
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
    resultList = []
    if request.method == 'GET':
        resultList = list(data)
    elif request.method == 'POST':
        size = request.data['size']
        start = request.data['start'] * size
        resultList = list(data)[start : start + size]
    return Response(resultList)

@api_view(['POSt'])
def getCatalogue(request):
    """
    获取某个新闻网站的类别列表
    :param request:
        {
            "source": "澎湃新闻"
        }
    :return:

    """
    source = request.data['source']
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


@api_view(['POST'])
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
    print request.data
    source = request.data['source']
    catalogue = request.data['catalogue']
    size = request.data['size']
    start = request.data['start'] * size
    #获取新闻的简要信息
    data = newsCol.find({"source": source, "catalogue": catalogue}, {"_id": 0}).skip(start).limit(size)
    resultList = list(data)
    print resultList
    return Response(resultList)

@api_view(['GET'])
def getNews(request, id):
    """
    根据id获取新闻
    :param request:
    :return: News Item

    """
    news = newsCol.find_one({'_id': ObjectId('5828343ffb6f8974f6b97794')})
    news['_id'] = str(news['_id'])
    return Response(news)

@api_view(['GET','POST'])
def getKeywords(request):
    """
    获取关键词
    :param request:
        {
            "start":0.
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
    if request.method == 'POST':
        size = request.data['size']
        start = request.data['start'] * size

    pipeline = [{
        "$project": {"keywords": 1, "title": 1}

    },{
        "$unwind": "$keywords",
    },{
        "$group": {"_id": "$keywords", "count": {"$sum": 1}}
    }]
    resultList = list(newsCol.aggregate(pipeline))
    return Response(resultList[start:size])

@api_view(['GET','POST'])
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
    if request.method == 'POST':
        size = request.data['size']
        start = request.data['start'] * size
        keyword = request.data['_id']
    resultList = list(newsCol.find({"keywords": keyword},{"_id": 0}))
    return Response(resultList)

class News(APIView):
    def get(self, request, format = None):
        data = db['news'].find_one({},{'_id':0})
        # data['_id'] = data['_id'].toString()
        # print data
        return Response(data)
        return HttpResponse(u"欢迎光临 自强学堂!")

