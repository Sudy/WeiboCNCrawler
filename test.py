#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import xmlrpclib

server = xmlrpclib.ServerProxy("http://192.168.3.48:8000")
print server.getAccount()