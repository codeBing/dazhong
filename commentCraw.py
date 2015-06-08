#-*- coding:utf-8 -*-
"根据shopid.txt文件中的商户id和名称抓取大众点评的点评详情"

__author__ = 'BING'

import urllib2
import cookielib
import re
import time
import codecs
import sys
import threading
from Queue import Queue
from bs4 import BeautifulSoup

import database

reload(sys)
sys.setdefaultencoding('utf8')

class commentCraw(threading.Thread):

    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.baseurl = 'http://t.dianping.com/ajax/detailDealRate?'
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.queue = queue

    #通过商户id号获取指定页的评论
    def getdeal(self,dealgroupid,pageno):
        try:
            cj = cookielib.CookieJar()
            cookiehandler = urllib2.HTTPCookieProcessor(cj)
            opener = urllib2.build_opener(cookiehandler)
            request = urllib2.Request(self.baseurl+'dealGroupId='+str(dealgroupid)+'&pageNo='+str(pageno),headers=self.headers)
            response = opener.open(request)
            content = response.read().decode('utf-8')
            soup = BeautifulSoup(content,'html.parser')
            if soup.find_all(class_='empty'):#找到empty类表示此页没有评论
                return None
            else:
                return content
        except urllib2.URLError, e:
            print e.reason
            #若被服务器识别出，则休眠5分钟再次发出请求
            time.sleep(300)
            self.getdeal(dealgroupid, pageno)
        except Exception, e:
            print e
            return None

    #获取指定商户id的所有评论
    def getcomment(self,dealgroupid,shopname):
        pageno = 1  
        while True:
            #循环请求指定商户的所有评论页面，知道返回None
            content = self.getdeal(dealgroupid,pageno)
            if content is None:
                break
            else:
                soup = BeautifulSoup(content, 'html.parser')
                comments = soup.find_all('div',class_='comment-body')
                for comment in comments:
                    pattern = re.compile('<span.*?class="syellowstar(\d)0.*?star-icon"></span>.*?<div.*?class="J_brief_cont_full.*?">(.*?)</div>',re.S)
                    items = re.findall(pattern, str(comment))
                    for item in items:
                        data = [shopname,item[0],item[1].strip('\n')]
                        mLock.acquire()
                        conn.insert(data)
                        mLock.release()
            pageno += 1

    #读取保存商户id和名称的文件，获取所有评论
    def run(self):
        print '线程开始工作'
        while True:
            dealgroupid, shopname = self.queue.get()
            self.getcomment(dealgroupid, shopname)
            self.queue.task_done()

if __name__ == '__main__':
    start = time.ctime()
    print start
    #同步锁
    mLock = threading.Lock()
    queue = Queue()
    comments = [i for i in codecs.open('shopid.txt', 'r', 'utf-8').readlines()]
    #将任务以tuple的形式放入队列中
    for comment in comments:
        shop = str(comment.strip())
        shop = shop.split('_')
        queue.put((shop[1], shop[0]))
    conn = database.database()
    conn.connect()
    #创建4个工作线程
    for x in range(4):
        commenthandler = commentCraw(queue)
        commenthandler.daemon = True
        commenthandler.start()
    queue.join()
    if conn.conn:
        conn.close()
    end = time.ctime()
    print end
    print end-start
