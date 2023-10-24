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


## 三、執行結果

![image-20231024151657622](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151657622.png)

![image-20231024151723585](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151723585.png)

![image-20231024151739537](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151739537.png)

![image-20231024151819996](https://raw.githubusercontent.com/Mark850409/UploadGithubImage/master/image-20231024151819996.png)
