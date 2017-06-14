def rbCity():  #點選縣市選項按鈕後處理函式
    global sitelist, rbtemSite ,frame2
    sitelist.clear() # 清除原有測站串列
    frame2.pack_forget()
    frame2.grid_forget()
    print(frame2)             
    
    for c1 in range(len(citylist)):  #逐一取出選取縣市的測站
        if(citylist[c1]['_id'] == city.get()):
             for s in citylist[c1]["SiteName"]:
                 sitelist.append(s)  
                 
    sitemake()  #建立測站選項按鈕
    rbSite()  #顯示各地雨量訊息

def rbSite():  #點選測站選項按鈕後處理函式
    global collection, now
    for s in sitelist:  #逐一取得測站
        if(s == site.get()):  #取得點選的測站
            res=collection.find({"County":city.get(),"SiteName":s,"PublishTime":maxtime})
            rainfall24 = res[0]["Rainfall24hr"]  #取得累計一天雨量的值
            rainfall3=res[0]["Rainfall3hr"]      #取得累計3hr雨量的值
            rainfall=res[0]["Rainfall1hr"]       #取得累計1hr雨量的值
            updateTime=res[0]["PublishTime"]
            if(pd.isnull(rainfall) or  pd.isnull(rainfall24) or pd.isnull(rainfall3) ):  #如果沒有資料
                result1.set(s + "站的 雨量目前無資料！")
            else:  #如果有資料
                if(float(rainfall24) >= 500):  #轉換為等級
                    grade1 = "超大豪雨"
                elif(float(rainfall24)>= 350):
                    grade1 = "大豪雨"
                elif(float(rainfall24)>= 200 or float(rainfall3) >=100):
                    grade1 = "豪雨"
                elif(float(rainfall24) >= 80 or float(rainfall) >=40):
                    grade1="大雨"
                elif(float(rainfall24) > 0):
                    grade1="局部陣雨"
                else:
                    grade1 = "無雨量"
                result1.set(s + "站的 當日累積雨量 值為「" + str(rainfall24) + "」：「" + grade1 + "」等級"+"，更新時間："+str(updateTime))

            break  #找到點選測站就離開迴圈
def clickRefresh():  #重新讀取資料
    global citylist ,maxtime,client
    citylist.clear() # 清除原有資料
    print(maxtime)
    print("refresh")
    db=client.csmu
    collection = db.rainlow

    for x in collection.aggregate([
        {
            "$group": {
                "_id": "$County",
                "SiteName": {
                    "$addToSet": "$SiteName"
                },
               "last" :{
                    "$max":"$PublishTime"
               }        
            }
        }
    ]):
        citylist.append(x)

    maxtime=citylist[0]['last']
    print(maxtime)
    rbSite()  #更新測站資料

def sitemake():  #建立測站選項按鈕
    global sitelist, rbtemSite, frame2
    
    frame2 = tk.Frame(win)  #測站容器
    frame2.pack() 
    
    for i in range(0,10):  #3列選項按鈕
        for j in range(0,10):  #每列8個選項按鈕
            n = i * 10+ j  #第n個選項按鈕
            if(n < len(sitelist)):
                rbtemSite = tk.Radiobutton(frame2, text=sitelist[n], variable=site, value=sitelist[n], command=rbSite)  #建立選項按鈕
                rbtemSite.grid(row=i, column=j)  #設定選項按鈕位置
            if(n==0):  #預設選取第1個項目         
                 rbtemSite.select()
   
     
def makeplot():
    global collection, now 
    indexs= ["10min","1hr","3hr","6hr","12hr","24hr","now"]
    columns=["mm"]
    for s in sitelist:  #逐一取得測站
        if(s == site.get()):  #取得點選的測站
            res=collection.find({"County":city.get(),"SiteName":s,"PublishTime":maxtime})
            datas=[float(res[0]["Rainfall10min"]),float(res[0]["Rainfall1hr"]),float(res[0]["Rainfall3hr"]),float(res[0]["Rainfall6hr"]),float(res[0]["Rainfall12hr"]),float(res[0]["Rainfall24hr"]),float(res[0]["Now"])]
    df=pd.DataFrame(datas,columns=columns,index=indexs)
    df.plot()       


import tkinter as tk
import pandas as pd
import time

from pymongo import MongoClient
client = MongoClient('127.0.0.1', 27017)# 連接Mongo資料庫
print (client)  #確認是否連接成功
db=client.csmu
collection = db.rainlow


             
win=tk.Tk()
win.geometry("960x720") 
win.title("每日雨量監測")

city = tk.StringVar()  #縣市文字變數
site = tk.StringVar()  #測站文字變數
result1 = tk.StringVar()  #訊息文字變數
citylist = []  #縣市串列
sitelist = []  #鄉鎮串列
listradio = []  #鄉鎮選項按鈕串列
# 開啟系統 首次find 
for s in collection.aggregate([
        {
            "$group": {
                "_id": "$County",
                "SiteName": {
                    "$addToSet": "$SiteName"
                },
               "last" :{
                    "$max":"$PublishTime"
               }        
            }
        }
    ]):
    citylist.append(s)
maxtime=citylist[0]['last']
print(maxtime)

label1 = tk.Label(win, text="縣市：", pady=6, fg="blue", font=("新細明體", 12))
label1.pack()
frame1 = tk.Frame(win)  #縣市容器
frame1.pack()
for i in range(0,3):  #3列選項按鈕
    for j in range(0,8):  #每列8個選項按鈕
        n = i * 8 + j  #第n個選項按鈕
        if(n < len(citylist)):
            city1 = citylist[n]["_id"]  #取得縣市名稱
            rbtem = tk.Radiobutton(frame1, text=city1, variable=city, value=city1, command=rbCity)  #建立選項按鈕
            rbtem.grid(row=i, column=j)  #設定選項按鈕位置
            if(n==0):  #選取第1個縣市
                rbtem.select()
                for s in citylist[n]["SiteName"]:
                 sitelist.append(s)  


btnDown = tk.Button(win, text="更新資料", font=("新細明體", 12), command=clickRefresh)
btnDown.pack(pady=6)
btnPlot = tk.Button(win, text="顯示圖表", font=("新細明體", 12), command=makeplot)
btnPlot.pack(pady=6)  
lblResult1 = tk.Label(win, textvariable=result1, fg="red", font=("新細明體", 16))
lblResult1.pack(pady=6)
label2 = tk.Label(win, text="測站：", pady=6, fg="blue", font=("新細明體", 12))
label2.pack()

sitemake()#顯示預設測站
rbSite()  #顯示測站訊息

win.mainloop()
