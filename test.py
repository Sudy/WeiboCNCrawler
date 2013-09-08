#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import pymongo
import re 
#p = re.compile("/u/([0-9]{8,10})")
#p = re.compile("/([A-Za-z0-9]+)\?vt")
#p = re.compile("/([0-9]+)")

p = re.compile("/(u/([0-9]{8,10}) | ([A-Za-z0-9]+)\?vt | ([0-9]+))")
print p.match("/u/4156589312?vt=4=").group(1)

