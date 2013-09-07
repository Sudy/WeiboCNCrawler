#!/usr/bin/env python
#-*- coding:utf-8 -*-

basedigits='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
BASE=len(basedigits)
 
 
def decode(s):
    ret,mult = 0,1
    for c in reversed(s):
        ret += mult*basedigits.index(c)
        mult *= BASE
    return ret
 
def encode(num):
    if num <0: raise Exception("positive number "+ num)
    if num ==0: return '0'
    ret=''
    while num != 0:
        ret = (basedigits[num%BASE])+ret
        num = int(num/BASE)
    return ret