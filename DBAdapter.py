#-*- encoding=utf-8 -*-

import pymongo


DBSERVER = "192.168.3.48"
DATABASE = "weibo"
WEIBOTABLE = "user_weibo"
ERRORTABLE = "error"


class _DBAdapter():
    def __init__(self):
        try:
            pycon = pymongo.Connection(host=DBSERVER,port=27017)
            self.dbWeiboTable = pycon[DATABASE][WEIBOTABLE]
            self.dbErrorTable = pycon[DATABASE][ERRORTABLE]
            
        except:
            print "connect to" + DBSERVER + "Failed"
    
    def insertWeibo(self,item):
        try:
            self.dbWeiboTable.insert(item)
        except:
            print "insert error ",item
    def insertError(self,item):
        try:
            self.dbErrorTable.insert(item)
        except:
            print "insert dbErrorTable error",item

if __name__ == "__main__":
    dbadapter = _DBAdapter()
    dbadapter.insertWeibo({"u":1,"b":2})