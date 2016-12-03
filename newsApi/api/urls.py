"""newsApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from api import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
    url(r'^$', views.index),
    url(r'^getNews/(?P<id>.+)', views.getNews),
    url(r'^getWechat/(?P<id>.+)', views.getWechat),
    url(r'^getSource', views.getSource),
    url(r'^getCatalogue', views.getCatalogue),
    url(r'^getNewsList', views.getNewsList),
    url(r'^getKeywords', views.getKeywords),
    url(r'^getNewsByKey', views.getNewsByKey),
    url(r'^getWechatSource', views.getWechatSource),
    url(r'^getWechatList', views.getWechatList),
    url(r'^news/$', views.News.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)