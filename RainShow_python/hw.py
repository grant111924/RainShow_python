# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:13:23 2017

@author: DELL
"""

import pandas as pd
import numpy as np
import urllib3 
import json
import time
from pymongo import MongoClient
n=0
while  True:
    n=n+1
    print(n)
    url="http://opendata.epa.gov.tw/webapi/api/rest/datastore/315070000H-000001?sort=PublishTime&offset=0&limit=1000"
    http=urllib3.PoolManager() # 開啟http
    getFile= http.request('GET',url) #發出GET請求 放入URL 
    #getFile.data 就是reponse
    data=json.loads(getFile.data.decode('utf-8')) #getFile.data 為回傳值 json.loads 讀取JSON  內有decode 解析utf8文件
    new_posts=data["result"]["records"] #從data變數中 解開JSON 內容
    # 連接Mongo資料庫
    client = MongoClient('127.0.0.1', 27017)
    print (client)  #確認是否連接成功
    db=client.csmu
    collection = db.rainlow
    # 輸入MongoDB語法
    result = collection.insert_many(new_posts)
    print(result)
    #每10分鐘抓一次資料
    time.sleep(600)




