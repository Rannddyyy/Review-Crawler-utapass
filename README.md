Uta Pass Review Crawler
===============================

<img src="https://img.au-market.com/mapi/pc_icon/39767/3976700000002/100211_116788.png" width="100">

Introduction
---

Uta Pass Review Crawler 是一支評價爬蟲，透過 [Slack - Incoming Webhooks](https://api.slack.com/incoming-webhooks) 將 Google Play / Au Market / Apple Store 上的 Uta Pass 評價推播至指定的 Slack 頻道或是人物。 


使用方法
---

### 初次使用

1. `$ export SLACK_HOOK_CRAWLER={Slack 的 HOOK URL}; export MONGODB_URL={MongoDB URL}`
2. `$ virtualenv venv`   // 建置虛擬環境
3. `$ source venv/bin/activate`   // 進入虛擬環境
4. `$ pip install -r requirements.txt`    // 安裝所有需要的套件

### 單次執行 
1. `$ source venv/bin/activate`
2. `$ python run.py`

### 排程定時執行

使用 [crontab](http://linux.vbird.org/linux_basic/0430cron.php#crontab) 進行排程

e.g. `*/5 * * * * source .../venv/bin/activate;python .../run.py` // 每 5 分鐘執行一次

可以將 log 寫入檔案，在最後加上 `>> {xxx.log 路徑} 2>&1` 即可

系統架構設計
---

+ 使用 Http requests 取得資料
    > - Google Play，使用 json.load 將 JSON 轉成 Python Dictionary
    > - Au Market，使用 BeautifulSoup 解析 HTML 資料
    > - Apple Store，使用 feedparser 解析 RSS 資料
+ 使用 [MongoDB](https://www.mongodb.com/) 作為資料庫 
+ 使用 [googletrans](https://pypi.org/project/googletrans/) 翻譯

Screenshots
---

 - Google Play 評價
 
 <img src="https://imgur.com/qOQHobW.png">
 
 
 - au Market 評價
 
 <img src="https://imgur.com/2u4RSDd.png">
 
 
 - Apple Store 評價
 
 <img src="https://imgur.com/0aTImzb.png">
 
 注意事項
 ---
 
Incoming Webhooks 使用的是[這隻](https://kkbox.slack.com/services/BBZKL3SPN)， 他的 Webhook URL 為 `https://hooks.slack.com/services/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`，只有建立者才能更改 Webhook 的設定，如果有操作上的需求，可以自己新建一隻 Incoming Webhooks。
 
Review Crawler 中的 Webhook URL 存放於 [RequestManager.py](/up-review-crawler/RequestManager.py)。
 
Reference
---

 - [30天之你好MongoDB系列](https://ithelp.ithome.com.tw/users/20089358/ironman/1064)
 - [Slcak - Incoming Webhooks](https://api.slack.com/incoming-webhooks)
 - [[教學] 如何透過webhook將訊息送進slack](https://xenby.com/b/139-%E6%95%99%E5%AD%B8-%E5%A6%82%E4%BD%95%E9%80%8F%E9%81%8Ewebhook%E5%B0%87%E8%A8%8A%E6%81%AF%E9%80%81%E9%80%B2slack)
