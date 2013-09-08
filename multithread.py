#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import xmlrpclib
import threading  
from weibocn import SimulateLoginer
from parser import Parser
import time
import random
import json


class Crawler(threading.Thread):
    #The timer class is derived from the class threading.Thread  
    def __init__(self):  
        threading.Thread.__init__(self)

        self.thread_stop = False
        #try up to five times to get a url seed
        self.try_get_url_seed = 0
        #connect the server
        self.server = xmlrpclib.ServerProxy("http://172.17.161.101:8000")


        self.parser = Parser()

        #function  map dealing with different type
        self.func_map = { 
        0:self.deal_type0,
        1:self.deal_type1,
        2:self.deal_type2,
        3:self.deal_type3,
        4:self.deal_type4,
        5:self.deal_type5
        }
        self.gsid = "4uNrb1c01QZjnhvLHZAmvarK09p"
        #self.get_an_gsid()

    def get_an_gsid(self):
        #get ussername and password
        usrname,passwd = self.server.getAccount()
        
        if (usrname,passwd) == (0,0):
            print "no more account available"
            self.thread_stop = True
            return 0

        #simulate the login process
        simulateLoginer = SimulateLoginer(usrname,passwd)        
        #login to the weibo and get gsid
        self.gsid = simulateLoginer.login()
        print self.gsid
        
        if 0 == self.gsid:
            time.sleep(3)
            self.get_an_gsid()

    #type 0 is the seed user
    '''
    postdata = {
            "base_url":"http://weibo.cn/u/",
            "uid":line,
            "vt":"4",
            "type":0
            }
    '''
    def deal_type0(self,postdata):
        
        #make the url
        url = postdata["base_url"]
        url += postdata["uid"] + "?"
        url += "vt=" + postdata["vt"] + "&"
        url += "gsid=" + self.gsid
        print "type0:",url 
        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_weibo_first_page(html,postdata["uid"])

    '''
        postdata = {
        "base_url":"http://weibo.cn/u/",
        "uid":uid,
        "page_num":page_num,
        "type":1
        }
    '''
    def deal_type1(self,postdata):
        #make the url
        url = postdata["base_url"]
        url += postdata["uid"] + "?"
        url += "vt=" + postdata["vt"] + "&"
        url += "page=" + postdata["page_num"] + "&"
        url += "gsid=" + self.gsid

        print "type1:",url
        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_weibo(html,postdata["uid"])

    '''
        postdata = {
        "base_url":"http://weibo.cn/comment/",
        "rl":"0",
        "vt":"4",
        "uid":uid,
        "cid":id,
        "type":2
        }
    '''
    def deal_type2(self,postdata):
        #http://weibo.cn/comment/A83UNd82V?uid=2200249730&rl=0&vt=4&gsid=4utD1a1a1I32ESqk4qGQpartGdX&st=af84#cmtfrm
        url = postdata["base_url"]
        url += postdata["cid"] + "?"
        url += "uid=" + postdata["uid"] + "&"
        url += "rl=" + postdata["rl"] + "&"
        url += "vt=" + postdata["vt"] + "&"
        url += "gsid=" + self.gsid 

        print "type2",url

        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_comment_firstpage(html,postdata["uid"],postdata["cid"])

    '''
        postdata = {
        "base_url":"http://weibo.cn/repost/",
        "rl":"0",
        "vt":"4",
        "uid":uid,
        "cid":id,
        "type":3
        }
    '''
    def deal_type3(self,postdata):
        url = postdata["base_url"]
        url += postdata["cid"] + "?"
        url += "uid=" + postdata["uid"] + "&"
        url += "rl=" + postdata["rl"] + "&"
        url += "vt=" + postdata["vt"] + "&"
        url += "gsid=" + self.gsid 
        print "type2",url
        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_repost_firstpage(html,postdata["uid"],postdata["cid"])

    '''
    postdata = {
        "base_url":"http://weibo.cn/comment/",
        "uid":uid,
        "cid":cid,
        "page_num":cnt_page_num,
        "type":4
        }
    '''
    def deal_type4(self,postdata):
        url = postdata["base_url"]
        url += postdata["cid"] + "?"
        url += "uid=" + postdata["uid"] + "&"
        url += "page=" + postdata["page_num"] + "&"
        url += "gsid=" + self.gsid 
        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_comment(html)


    '''
    postdata = {
        "base_url":"http://weibo.cn/repost/",
        "uid":uid,
        "cid":cid,
        "page_num":repost_page_num,
        "type":5
    }
    '''
    def deal_type5(self,postdata):
        url = postdata["base_url"]
        url += postdata["cid"] + "?"
        url += "uid=" + postdata["uid"] + "&"
        url += "page=" + postdata["page_num"] + "&"
        url += "gsid=" + self.gsid 
        html = self.parser.get_html_content(url,0)
        if None != html:
            self.parser.parse_repost(html)
                                        
    def run(self):
     #Overwrite run() method, put what you want the thread do here  
        while not self.thread_stop and self.try_get_url_seed < 5:  
            
            item = self.server.removeFromQueue()
            print "item got from dispatcher",item
            #no more urls
            if 0 == item:
                time.sleep(5)
                self.try_get_url_seed += 1
                continue
            else:
                #deal with the data
                json_data = json.loads(item)
                self.func_map[int(json_data["type"])](json_data)
                time.sleep(random.randint(3,5))


    def stop(self):  
        self.thread_stop = True


if __name__ == "__main__":
    #for i in range(0,1):
    thread = Crawler()
    thread.start()
    #    print "thread  " + str(i) + "started"
    #    time.sleep(1)  