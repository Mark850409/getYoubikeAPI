### 簡介

透過`政府開放資料平台`取得資料，並透過`SP寫入資料庫`，然後`寄信通知`使用者

### 專案結構

```
20231024_getYoubikeAPI
├─ email.properties
├─ getYoubikeAPI.ipynb
├─ getYoubikeAPI.py
├─ logging_config.ini
├─ logs
│  ├─ 2023-10-24_getAPIYoubikeData.csv
│  └─ getAPIYouBikeData.log
├─ my_config.ini
└─ README.md
```

### 目錄
- [一、使用方式](#一使用方式)
  - [(1) 注意事項](#1-注意事項)
  - [(2) 操作步驟](#2-操作步驟)
- [二、執行步驟](#二執行步驟)
- [三、執行結果](#三執行結果)


## 一、使用方式

### (1) 注意事項
1. 因為`git公開專案`很危險，所以我把設定檔的`帳密全部拿掉`，測試時請再加上。
2. 如果測試時發現有`某個套件有少`，例如no module...的訊息，請自行google套件`安裝方式`。
3. 請確定自己的`本機`或是`伺服器`環境有`安裝Python`。
4. email的話我是用gmail，gmail目前的`認證機制`有改，請自行搜尋如何`建立二階段驗證`密碼，取得密碼後填入`email.properties`的`password`。

### (2) 操作步驟
1. 進入以下網址 https://github.com/Mark850409/getYoubikeAPI 。
2. 進入到畫面可看到右上方code按鈕，請點一下。
3. 點擊DownloadZIP，此時會跳出下載視窗，請自行選擇存放目錄。
4. 解壓後就可以開始使用此專案。


## 二、執行步驟

1. 開啟`my_config.ini`，輸入以下內容
- username = 你的使用者名稱
- password = 你的使用者密碼
- db = 你的資料庫名稱
- host = 你的資料庫主機ip(網域名)
- port = 你的資料庫主機的port(一般MySQL是3306)

2. 開啟`email.properties`，輸入以下內容
- host = smtp.gmail.com
- port = 587
- subject = 主旨(可以隨意更改)
- from = 寄件人地址
- to = 收件人地址
- body = 信件主體(可以隨意更改)
- account = 電子郵件帳號
- password = 電子郵件密碼
- dir_path = 郵件附加檔案目錄的位址(要改成你自己的)

3. `logging_config.ini`，這個是每次執行程式都會有個`log紀錄`，這是`設定檔`，如果不確定怎麼改可以`google`，或是`先不動`用我的設定也可以。

4. 撰寫setYoubikeData `STORE PROCEDURE`，輸入以下程式碼

```sql
DELIMITER $$
-- 如果PROCEDURE存在就先移除                                                                                                                                                                   
DROP PROCEDURE IF EXISTS setYoubikeData $$       
-- 建立PROCEDURE(傳入API參數，欄位數量要一致喔)                                                                                                                           
CREATE PROCEDURE setYoubikeData(IN `sno` INT, IN `sna` VARCHAR(200), IN `tot` INT, IN `sbi` INT, IN `sarea` VARCHAR(50), IN `mday` VARCHAR(50), IN `lat` DOUBLE, IN `lng` DOUBLE, IN `ar` VARCHAR(200), IN `sareaen` VARCHAR(200), IN `snaen` VARCHAR(200), IN `aren` VARCHAR(200), IN `bemp` VARCHAR(200), IN `act` VARCHAR(50), IN `srcUpdateTime` VARCHAR(50), IN `updateTime` VARCHAR(50), IN `infoTime` VARCHAR(50), IN `infoDate` VARCHAR(50))  
BEGIN
-- 不存在的話建立getdata資料表() 
CREATE TABLE IF NOT EXISTS getdata(  
    sno INT,
    sna char(200),
    tot INT,
    sbi INT,
    sarea char(50),
    mday char(50),
    lat double,
    lng double,
    ar char(50),
    sareaen char(200),
    snaen char(200),
    aren char(200),
    bemp char(200),
    act char(200),
    srcUpdateTime char(200),
    updateTime char(200),
    infoTime char(200),
    infoDate char(200)
); 
-- 將API的資料寫入getdata(傳入API參數，欄位數量要一致喔)
INSERT INTO getdata VALUES(sno,sna,tot,sbi,sarea,mday,lat,lng,ar,sareaen,snaen,aren,bemp, act,srcUpdateTime,updateTime,infoTime,infoDate);
END$$
DELIMITER ;

```

5. 撰寫`getYoubikeAPI.py`，輸入以下程式碼
```python
#!/usr/bin/env python
# coding: utf-8
import configparser
import csv
import json
import logging
import os
import smtplib
import sys
import urllib.request as req
from datetime import date, datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging.config import fileConfig

import mysql.connector
from MySQLdb import Error
from pyjavaproperties import Properties

# 取得LOG設定檔
fileConfig("logging_config.ini", encoding="utf-8")
logger = logging.getLogger()
# 取得今天日期
today = date.today().isoformat()
# 取得資料庫設定檔
config = configparser.ConfigParser()
config.read("my_config.ini")

# 宣告全域變數
global result, connection, cursor
# 讀取資料庫變數
username = config.get("DB", "username")
password = config.get("DB", "password")
db = config.get("DB", "db")
host = config.get("DB", "host")
port = config.get("DB", "port")
# 資料庫設定
db_settings = {
    "host": host,
    "port": port,
    "user": username,
    "password": password,
    "db": db,
    "charset": "utf8",
    "auth_plugin": "mysql_native_password",
}

# 主程式(將API相關欄位取出並寫入CSV&資料庫)
def getOpenData(url3):
    with req.urlopen(url3) as res3:
        data3 = json.load(res3)
    try:

        with open(
            "./logs/" + today + "_getAPIYoubikeData.csv",
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            num = 0
            logger.info(f"開始寫入CSV")
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "站點代號",
                    "場站中文名稱",
                    "場站總停車格",
                    "場站目前車輛數量",
                    "場站區域",
                    "資料更新時間",
                    "緯度",
                    "經度",
                    "地點",
                    "場站區域英文",
                    "場站名稱英文",
                    "地址英文",
                    "空位數量",
                    "全站禁用狀態",
                    "YouBike2.0系統發布資料更新的時間",
                    "大數據平台經過處理後將資料存入DB的時間",
                    "各場站來源資料更新時間",
                    "各場站來源資料更新時間",
                ]
            )
            logger.info(f"標題寫入完成")
            logger.info(f"開始執行批次...")
            for stitle in data3:
                num = num + 1
                sno = stitle["sno"]
                sna = stitle["sna"]
                tot = stitle["tot"]
                sbi = stitle["sbi"]
                sarea = stitle["sarea"]
                mday = stitle["mday"]
                lat = stitle["lat"]
                lng = stitle["lng"]
                ar = stitle["ar"]
                sareaen = stitle["sareaen"]
                snaen = stitle["snaen"]
                aren = stitle["aren"]
                bemp = stitle["bemp"]
                act = stitle["act"]
                srcUpdateTime = stitle["srcUpdateTime"]
                updateTime = stitle["updateTime"]
                infoTime = stitle["infoTime"]
                infoDate = stitle["infoDate"]
                writer.writerow(
                    [
                        sno,
                        sna,
                        tot,
                        sbi,
                        sarea,
                        mday,
                        lat,
                        lng,
                        ar,
                        sareaen,
                        snaen,
                        aren,
                        bemp,
                        act,
                        srcUpdateTime,
                        updateTime,
                        infoTime,
                        infoDate,
                    ]
                )
                call_accessionsByaffliction(
                        sno,
                        sna,
                        tot,
                        sbi,
                        sarea,
                        mday,
                        lat,
                        lng,
                        ar,
                        sareaen,
                        snaen,
                        aren,
                        bemp,
                        act,
                        srcUpdateTime,
                        updateTime,
                        infoTime,
                        infoDate,
                )
        logger.info(f"資料寫入完成...")
        csv_file.close()

    except OSError as e:
        logging.debug("Catch an exception.", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logging.debug("Catch an exception.", exc_info=True)
        sys.exit(1)


# 寄信程式
def sendGmailwithattachment():
    email = Properties()
    email.load(open("email.properties", encoding="utf-8"))
    with smtplib.SMTP(host=email["host"], port=email["port"]) as smtp:  # 設定SMTP伺服器
        try:
            logger.info(f"開始寄信...")
            content = MIMEMultipart()  # 建立MIMEMultipart物件
            content["subject"] = email["subject"]  # 郵件標題
            content["from"] = email["from"]  # 寄件者
            content["to"] = email["to"]  # 收件者
            content.attach(MIMEText(email["body"]))  # 郵件內容
            dir_path = email["dir_path"]
            files = [today + "_getAPIYoubikeData.csv", "getAPIYouBikeData.log"]
            for f in files:  # add files to the message
                file_path = os.path.join(dir_path, f)
                attachment = MIMEApplication(
                    open(file_path, "rb").read(), _subtype="txt"
                )
                attachment.add_header("Content-Disposition", "attachment", filename=f)
                content.attach(attachment)
            logger.info(f"附加檔案加入成功...")
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(email["account"], email["password"])  # 登入寄件者gmail
            logger.info(f"寄信成功...")
            smtp.send_message(content)  # 寄送郵件
            
        except Exception as e:
            logging.debug("Catch an exception.", exc_info=True)
            logger.error(e)


# 建立資料庫連線&呼叫批次
def call_accessionsByaffliction(
    sno,
    sna,
    tot,
    sbi,
    sarea,
    mday,
    lat,
    lng,
    ar,
    sareaen,
    snaen,
    aren,
    bemp,
    act,
    srcUpdateTime,
    updateTime,
    infoTime,
    infoDate,
):
    try:
        # 連接 MySQL/MariaDB 資料庫
        connection = mysql.connector.connect(**db_settings)  # 密碼
        cursor = connection.cursor()
        if connection.is_connected():
            cursor.callproc(
                "setYoubikeData",
                (
                    sno,
                    sna,
                    tot,
                    sbi,
                    sarea,
                    mday,
                    lat,
                    lng,
                    ar,
                    sareaen,
                    snaen,
                    aren,
                    bemp,
                    act,
                    srcUpdateTime,
                    updateTime,
                    infoTime,
                    infoDate,
                ),
            )
            connection.commit()
    except Error as e:
        logger.info(f"資料庫連接失敗!!!", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 取得政府公開資料平台API
getOpenData(
    "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
)
# 使用GMAIL寄信
sendGmailwithattachment()
```


6. 在`VSCODE`或是其他的`IDE`執行python即可。


## 三、執行結果

![image-20231024151657622](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151657622.png)

![image-20231024151723585](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151723585.png)

![image-20231024151739537](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151739537.png)

![image-20231024151819996](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151819996.png)
