#!/usr/bin/env python
#-*- encoding=utf-8 -*-

import re
p = re.compile("M_([A-Za-z0-9]{5,9})")
print p.match("M_12323666").group(1)
