#!/usr/bin/env python
# coding: utf-8

# In[2]:


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


# In[ ]:




