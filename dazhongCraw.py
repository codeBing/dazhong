#-*- coding:utf-8 -*-
"根据链接获取大众点评指定地区和分类下的所有团购商户的id和名称，并保存到shopid.txt中，可供下一步获取评论详情所用"

__author__ = 'BING'

import urllib2
import re
import codecs
import time
import cookielib
import proxyIP,random,user_agents

from bs4 import BeautifulSoup

class CategoryCraw(object):

    shopId = set([])

    def __init__(self):
        self.baseUrl = 'http://t.dianping.com'
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.pagecount = 50

    #获取指定大分类下的所有小分类
    def getcategory(self):
        content = self.getpage(0)
        soup = BeautifulSoup(content, "lxml")
        soup = soup.find('div', id='classify')
        items = soup.find_all('a',href=re.compile('^/list/\w*-category_\d{1,3}$'))
        self.urlcategory = set([])
        for item in items:
            self.urlcategory.add(item['href'])

    #抓取指定链接的页面
    def getpage(self, index, url='/list/shenzhen-category_1'):
        try:
            #可以存储一定的代理服务器，每次随机选一个防止访问频繁被识别
            #proxy_ip =random.choice(proxyIP.proxy_list) #在proxy_list中随机取一个ip
            #proxy_support = urllib2.ProxyHandler(proxy_ip)
            cj = cookielib.CookieJar()
            cookile_support = urllib2.HTTPCookieProcessor(cj)
            #opener = urllib2.build_opener(cookile_support，proxy_support)
            opener = urllib2.build_opener(cookile_support)
            urllib2.install_opener(opener)
            trueurl = self.baseUrl+url+'?pageIndex='+str(index)
            request = urllib2.Request(trueurl)
            #可以存储一定的user_agent，每次随机选一个
            user_agent = random.choice(user_agents.user_agents)  #在user_agents中随机取一个做user_agent
            request.add_header('User-Agent',user_agent) #修改user-Agent字段
            response = urllib2.urlopen(request, timeout=60)
            content = response.read().decode('utf-8')
            return content
        except urllib2.URLError, e:
            print e.reason
            self.getpage(index, url)
        except Exception, e:
            print e.message
            self.getpage(index, url)

    #获取所有的商户id和名称
    def getid(self):
        for url in self.urlcategory:
            for index in range(0, self.pagecount):
                content = self.getpage(index,url)
                soup = BeautifulSoup(content,'html.parser')
                items = soup.find_all('a', class_='tg-floor-title', href=re.compile('^/deal/\d+$'))
                with codecs.open('shopid.txt','a','utf-8') as f:
                    for item in items:
                        name = item.find('h3').string
                        id = item['href']
                        id = id[6:]
                        if id not in CategoryCraw.shopId:
                            CategoryCraw.shopId.add(id)
                            f.write(name+'_'+id+'\r\n')


if __name__ == '__main__':
    starttime = time.ctime()
    print starttime
    work = CategoryCraw()
    work.getcategory()
    work.getid()
    endtime = time.ctime()
    print endtime
    print 'use time:',endtime-starttime


