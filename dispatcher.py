#!/usr/bin/env python
#-*- coding:utf-8 -*-
from SimpleXMLRPCServer import SimpleXMLRPCServer
from Queue import Queue
import json

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
			self.addToQueue(json.dumps(postdata))
		fp.close()
		print "initSeedUser successful"
		
	def addToQueue(self,postdata):

		json_data = json.loads(postdata)

		if 2 == json_data["type"]:
			cids = json_data["cid"]
			for item in cids:
				json_data["cid"] = item
				#crawl its comment
				json_data["base_url"] = "http://weibo.cn/comment/"
				json_data["type"] = 2
				print "seed data", json_data,"add to queue"
				self.url_queue.put(json.dumps(json_data))

				#crawl its repost
				json_data["base_url"] = "http://weibo.cn/repost/"
				json_data["type"] = 3
				print "seed data ",json_data,"add to queue"
				self.url_queue.put(json.dumps(json_data))
		else:
			print "seed data ",postdata,"add to queue"
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
			print "current size" + str(self.url_queue.qsize() - 1)

			postdata =  json.loads(self.url_queue.get())

			#save the value to old_postdata
			old_postdata = postdata
			#if there is a page num
			if postdata["type"] in [1,4,5] and int(postdata["page_num"])  > 1:
				#change the page_num value and save it back
				postdata["page_num"] = str(int(postdata["page_num"]) - 1)
				self.addToQueue(json.dumps(postdata))  
			return json.dumps(old_postdata)


server = SimpleXMLRPCServer(("192.168.3.48",8000),allow_none = True)
server.register_instance(Dispatcher())
server.serve_forever()