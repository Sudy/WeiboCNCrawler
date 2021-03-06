#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import urllib2
import urllib
import cookielib
import lxml.html as HTML
import re

class SimulateLoginer(object):
	def __init__(self, username=None, pwd=None):

		#browser proxy
		self.headers= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}

		self.username = username
		self.passwd = pwd
		
	#get the params hidden in the login page
	#using xpath methods  
	def get_param(self):
		login_url = 'http://login.weibo.cn/login/?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='

		#open login url
		req = urllib2.Request(login_url,urllib.urlencode({}), self.headers)
		resp = urllib2.urlopen(req)
		login_page = resp.read()
		#parse the login page
		action = HTML.fromstring(login_page).xpath("//form/@action")[0]
		passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
		vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
		return action, passwd, vk

	def login(self, username=None, pwd=None):
		if self.username is None or self.passwd is None:
			self.username = username
			self.passwd = pwd
		action, passwd, vk = self.get_param()

		data = urllib.urlencode({'mobile': self.username,
								  passwd: self.passwd,
								 'remember': 'on',
								 'backURL': 'http://weibo.cn/',
								 'backTitle': '新浪微博',
								 'vk': vk,
								 'submit': '登录',
								 'encoding': 'utf-8'})

		url = 'http://login.weibo.cn/login/' + action

		#login
		req = urllib2.Request(url, data, self.headers)
		resp = urllib2.urlopen(req)
		page = resp.read()
		
		#get the redirect link
		redirect_link = self.redirect(page)

		#get the gsid which is similar to token
		return self.get_gsid(redirect_link)

	def redirect(self,page):
		
		#get the redirect data
		redirect_link = HTML.fromstring(page).xpath("//a/@href")[0]

		if not redirect_link.startswith('http://'):
			redirect_link = 'http://weibo.cn/%s' % redirect_link

		req = urllib2.Request(redirect_link, headers=self.headers)
		urllib2.urlopen(req)
		return redirect_link

	#find the gsid 
	def get_gsid(self,redirect_link):
		pattern = re.compile("gsid=(.*?)&")
		
		gsid = 0
		try:
			gsid = pattern.search(redirect_link).group(1)
		except:
			gsid = 0
		
		return gsid


if __name__ == '__main__':
	f = SimulateLoginer("weibotest0002@163.com","iamwangbiao")
	print f.login()