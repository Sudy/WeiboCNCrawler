#!/usr/bin/env python
#-*- coding:utf-8 -*-
from SimpleXMLRPCServer import SimpleXMLRPCServer
from Queue import Queue

class Dispatcher(object):

	"""docstring for Dispatcher"""
	def __init__(self):
		#a infinit queue
		self.url_queue = Queue(maxsize=0)
		self.account_queue = Queue(maxsize = 0)
		
		self.initAvailableAccount()
		self.initSeedUser()

	#get all the available account
	def initAvailableAccount(self):
		fp = open("account","r")
		line = fp.readline()
		
		while "" != line and not line.startswith("#"):
			line = line.strip().split("\t",1)
			self.account_queue.put((line[0],line[1]))
			line = fp.readline()
		fp.close()
		print "initAvailableAccount successful"

	#get all the seed users
	def initSeedUser(self):
		#get all the available seed
		fp = open("seed","r")
		line = fp.readline()
		
		while "" != line and not line.startswith("#"):
			
			postdata = {
			"base_url":"http://weibo.cn/u/",
			"uid":line.strip(),
			"vt":"4",
			"type":0
			}
			line = fp.readline()
			self.addToQueue(postdata)
		fp.close()
		print "initSeedUser successful"
		
	def addToQueue(self,postdata):
		
		print postdata

		if 2 == postdata["type"]:
			weibo_ids = postdata["weibo_ids"]
			postdata.pop("weibo_ids")
			
			for item in weibo_ids:
				postdata["cid"] = item
				#crawl its comment
				postdata["base_url"] = "http://weibo.cn/comment/"
				postdata["type"] = 2

				self.addToQueue(postdata)
				#crawl its repost
				postdata["base_url"] = "http://weibo.cn/repost/"
				postdata["type"] = 3
				print postdata
				self.addToQueue(postdata)
		else:
			self.url_queue.put(postdata)

	def getAccount(self):
		if True == self.account_queue.empty():
			return 0,0
		else:
			return self.account_queue.get()


	#if the queue is empty and
	#the client have tried more five time
	def removeFromQueue(self):
		if True == self.url_queue.empty():
			return 0
		else:
			print "current size" + str(self.url_queue.size() - 1)
			postdata =  self.url_queue.get()
			#if there is a page num
			if postdata["type"] in [1,4,5] and int(postdata["page_num"])  > 1:
				#save the value to old_postdata
				old_postdata = postdata
				#change the page_num value and save it back
				postdata["page_num"] = str(int(postdata["page_num"]) - 1)
				self.addToQueue(postdata)  



dispatcher = Dispatcher()
server = SimpleXMLRPCServer(("192.168.3.48",8000))
server.register_instance(dispatcher)
server.serve_forever()