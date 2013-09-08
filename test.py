#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import pymongo
import re
import xmlrpclib

#p = re.compile("/u/([0-9]{8,10})")
#p = re.compile("/([A-Za-z0-9]+)\?vt")
#p = re.compile("/([0-9]+)")

#p = re.compile("/(u/([0-9]{8,10}) | ([A-Za-z0-9]+)\?vt | ([0-9]+))")
#print p.match("/u/4156589312?vt=4=").group(1)
'''
fp = open("account","r")
line = fp.readline()

while "" != line and not line.startswith("#"):
	line = line.strip().split("\t",1)
	print line
	line = fp.readline()
fp.close()
print "initAvailableAccount successful"
'''

server = xmlrpclib.ServerProxy("http://192.168.3.48:8000")
print server.getAccount()