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


@api_view(['GET'])
def sourceList(request):
    """
    获取新闻列表
    :param request:
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
    resultList = list(data)
    return Response(resultList)

@api_view(['GET'])
def getNews(request, id):
    """
    获取新闻
    :param request:
    :return: News Item

    """
    news = newsCol.find_one({'_id': ObjectId('5828343ffb6f8974f6b97794')})
    news['_id'] = str(news['_id'])
    return Response(news)


class News(APIView):
    def get(self, request, format = None):
        data = db['news'].find_one({},{'_id':0})
        # data['_id'] = data['_id'].toString()
        # print data
        return Response(data)
        return HttpResponse(u"欢迎光临 自强学堂!")

