#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import xmlrpclib
import threading  
from weibocn import SimulateLoginer
from parser import Parser
import time

class Crawler(threading.Thread):
    #The timer class is derived from the class threading.Thread  
    def __init__(self):  
        threading.Thread.__init__(self)

        self.thread_stop = False
        #try up to five times to get a url seed
        self.try_get_url_seed = 0
        #connect the server
        server = xmlrpclib.ServerProxy("http://192.168.3.48:8000")


        self.parse = Parser()

        #function  map dealing with different type
        self.func_map = { 
        0:self.deal_type0,
        1:self.deal_type1,
        2:self.deal_type2,
        3:self.deal_type3,
        4:self.deal_type4,
        4:self.deal_type5,
        }

    def get_an_gsid(self):
        #get ussername and password
        usrname,passwd = server.getAccount()
        
        if usrname,passwd == 0,0:
            print "no more account available"
            self.thread_stop = True

        #simulate the login process
        simulateLoginer = SimulateLoginer(usrname,passwd)        
        #login to the weibo and get gsid
        self.gsid = simulateLoginer.login()
        
        if 0 == self.gsid:
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
        url += self.gsid
        print "type0:",url 
        html = self.parser.get_html_content(url)
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
        url += "page=" + postdata[page_num] + "&"
        url += self.gsid

        print "type1:",url
        html = self.parser.get_html_content(url)
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
        url += self.gsid 

        print "type2",url

        html = self.parser.get_html_content(url)
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
        url += self.gsid 
        print "type2",url
        html = self.parser.get_html_content(url)
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
        url += "rl=" + postdata["rl"] + "&"
        url += "vt=" + postdata["vt"] + "&"
        url += "page=" + postdata["page_num"] + "&"
        url += self.gsid 
        html = self.parser.get_html_content(url)
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
        url += "rl=" + postdata["rl"] + "&"
        url += "vt=" + postdata["vt"] + "&"
        url += "page=" + postdata["page_num"] + "&"
        url += self.gsid 
        html = self.parser.get_html_content(url)
        self.parser.parse_comment(html)
        pass
                                        
    def run(self):
     #Overwrite run() method, put what you want the thread do here  
        while not self.thread_stop and self.try_get_url_seed < 5:  
            
            item = server.get()
            #no more urls
            if 0 == item:
                time.sleep(5)
                self.try_get_url_seed += 1
                continue
            else:
                #deal with the data
                self.func_map[item["type"]](item)


    def stop(self):  
        self.thread_stop = True  