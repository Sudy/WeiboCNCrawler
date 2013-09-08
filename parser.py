#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import urllib2
import lxml.html as HTML
import re
import xmlrpclib
import json
from DBAdapter import _DBAdapter

class Parser(object):
	"""docstring for Parser"""
	def __init__(self):
		self.headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}

		self.xpath_rule = {"post_time":"//div[@class='c']/div/span[@class='ct']/text()",
						   "weibo_content":"//div[@class='c']/@id | //div[@class='c']/div/span[@class='ctt']//text()",
						   "repostetc":"//div[@class='c']/div[last()]/a[position()>last()-4]/text()",
						   "page_num":"//input[@name='mp']/@value",
						   "comment_content":"//div[@class='c']/@id | //div[@class='c']/span[@class='ctt']//text()",
						   "user_id":"//div[@class='c']/a[position()=1]/@href | //div[@class='c']/a[position()=1]/text()",
						   "repost_time":"//div[@class='c']/span[@class='ct']/text()",
						   "repost_content":"//div[@class='c']//text()[not(parent::span)]"
		}

		self.mid_pattern = re.compile("M_([A-Za-z0-9]{5,9})")
		self.cid_pattern = re.compile("C_([0-9]{16})")
		#self.uid_pattern = re.compile("/(u/([0-9]{10}) | ([A-Za-z0-9])+)?vt | ([0-9]+))")
		self.server = xmlrpclib.ServerProxy("http://192.168.3.48:8000")
		self.dbadapter = _DBAdapter()


    #get html content of a given url
	def get_html_content(self,url,trytime):

		if trytime > 5:
			print "try " + url + " for more than five times"
			return None
		try:
			print "get_html_content ",url
			req = urllib2.Request(url, headers=self.headers)
			return urllib2.urlopen(req,timeout=10).read()
		except:
			self.get_html_content(url,trytime + 1)
		

	def get_post_time(self,html):
		time = HTML.fromstring(html).xpath(self.xpath_rule["post_time"])
		#[i.split(" ") for i in time]
		return time


	def get_post_uid(self,html):
		uid  = HTML.fromstring(html).xpath(self.xpath_rule["user_id"])
		return uid[2:-2]

	def get_repost_time(self,html):
		uid  = HTML.fromstring(html).xpath(self.xpath_rule["repost_time"])
		return uid

	def get_comment_content(self,html):
		comm_cnt = HTML.fromstring(html).xpath(self.xpath_rule["comment_content"])
		return self.deal_id_content(comm_cnt[1:],self.cid_pattern)

	def get_repost_content(self,html):
		repost_cnt = HTML.fromstring(html).xpath(self.xpath_rule["repost_content"])
		return repost_cnt[3:]
   
	def get_weibo_content(self,html):
		#get weibo content
		ctt = HTML.fromstring(html).xpath(self.xpath_rule["weibo_content"])
		return self.deal_id_content(ctt,self.mid_pattern)
			
	def get_repostetc(self,html):
		num = HTML.fromstring(html).xpath(self.xpath_rule["repostetc"])
		repostetc = list()
		for i in range(0,len(num)-1):
			if 3 != i%4:
				repostetc.append(num[i])
		return repostetc#[0::4]

	def get_page_num(self,html):
		page_num = HTML.fromstring(html).xpath(self.xpath_rule["page_num"])
		
		if 0 < len(page_num) and int(page_num[0]) > 1:
			return page_num[0]
		else:
			return 0
	def deal_id_content(self,ctt,pattern):

		id_cnt = list()
		content = str()

		for ct in ctt:
			#match the mid 
			#add mid and weibo content to list id_cnt
			mid_match = pattern.match(ct)

			if None != mid_match:
				if "" != content:
					id_cnt.append(content)
					content = ""
				id_cnt.append(mid_match.group(1))
			elif "" != ct:
				content += ct.strip()
		if "" != content:
			id_cnt.append(content)	
		return id_cnt

	def parse_weibo(self,html,uid):
		print "parse_weibo"	
		#mid,content
		mid_content = self.get_weibo_content(html)
		#comment,repost,like num
		repostetc =  self.get_repostetc(html)
		#post time
		post_time = self.get_post_time(html)

		#result
		total_item_num = len(post_time)
		#u:uid  m:mid c:content
		#r:repost l:like co:comment
		#t:time 
		data_to_db = {
			"u":uid,  
			"m":"",	
			"c":"", 
			"r":"", 
			"l":"",
			"co":"",
			"t":""
		}
		if len(mid_content) and len(repostetc) and total_item_num:
			for i in range(0,len(post_time) - 1):
				data_to_db["m"] = mid_content[2*i]
				data_to_db["c"] = mid_content[2*i + 1]
				data_to_db["r"] = repostetc[3*i] 
				data_to_db["co"] = repostetc[3*i + 1]
				data_to_db["l"] = repostetc[3*i + 2]
				data_to_db["t"] = post_time[i]
				self.dbadapter.insertWeibo(data_to_db)


			postdata = {
			"base_url":"",
			"rl":"0",
			"vt":"4",
			"uid":uid,
			"mid":mid_content[::2],
			"type":2
			}
			
			self.server.addToQueue(json.dumps(postdata))


	def parse_weibo_first_page(self,html,uid):
		print "parse_weibo_first_page"
		self.parse_weibo(html,uid)
		page_num = self.get_page_num(html)
		
		if int(page_num) > 1:
			#base_url,max_page,type
			postdata = {
			"base_url":"http://weibo.cn/u/",
			"uid":uid,
			"vt":"4",
			"page_num":page_num,
			"type":1
			}
			#print postdata
			self.server.addToQueue(json.dumps(postdata))
			
			

	def parse_repost(self,html,uid,mid):
		print "parse_repost"
		uid_name = self.get_post_uid(html)
		repost_content = self.get_repost_content(html)
		post_time = self.get_repost_time(html)
		#u:uid  m:mid 
		#un:username n:nickname co:comment
		#t:time
		data_to_db = {
			"u":uid,
			"m":mid,
			"un":"",
			"n":"",
			"co":"",
			"t":""
		}
		if len(uid_name) and len(repost_content) and len(post_time):
			for i in range(0,len(post_time) - 1):
				data_to_db["un"] = uid_name[2*i]
				data_to_db["n"] = uid_name[2*i + 1]
				data_to_db["co"] = repost_content[i]
				data_to_db["t"] = post_time[i]
				self.dbadapter.insertWeibo(data_to_db)
		


	def parse_repost_firstpage(self,html,uid,mid):
		print "parse_repost_firstpage"
		self.parse_repost(html,uid,mid)
		repost_page_num = self.get_page_num(html)

		if int(repost_page_num) > 1:
			postdata = {
			"base_url":"http://weibo.cn/repost/",
			"uid":uid,
			"mid":mid,
			"page_num":repost_page_num,
			"type":5
			}
			
			#print postdata
			self.server.addToQueue(json.dumps(postdata))
		


	def parse_comment(self,html,uid,mid):
		print "parse_comment"
		content = self.get_comment_content(html)
		uid_name = self.get_post_uid(html)
		post_time = self.get_post_time(html)
		#u:uid  m:mid 
		#un:username n:nickname co:comment
		#t:time
		data_to_db = {
			"u":uid,
			"m":mid,
			"un":"",
			"n":"",
			"co":"",
			"t":""
		}
		if len(uid_name) and len(content) and len(post_time):
			for i in range(0,len(post_time) - 1):
				data_to_db["un"] = uid_name[2*i]
				data_to_db["n"] = uid_name[2*i + 1]
				data_to_db["co"] = content[i]
				data_to_db["t"] = post_time[i]
				self.dbadapter.insertWeibo(data_to_db)
		

	def parse_comment_firstpage(self,html,uid,mid):
		self.parse_comment(html,uid,mid)
		cnt_page_num = self.get_page_num(html)
		
		if int(cnt_page_num) > 1:
			postdata = {
			"base_url":"http://weibo.cn/comment/",
			"uid":uid,
			"mid":mid,
			"page_num":cnt_page_num,
			"type":4
			}
			print "parse_comment_firstpage"
			#print postdata
			self.server.addToQueue(json.dumps(postdata))


	def test(self):
		req = urllib2.Request("http://weibo.cn/repost/2xcxW?uid=1710546672&rl=0&vt=4&gsid=4uNrb1c01QZjnhvLHZAmvarK09p",\
			headers=self.headers)
		html_text = urllib2.urlopen(req).read()

		ctt = self.get_post_uid(html_text)
		print ctt
		for c in ctt:
			print c
		
if __name__ == '__main__':
	p = Parser()
	p.test()