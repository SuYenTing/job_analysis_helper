# 職缺小幫手網站

## 一、簡介

這是一個簡單的職缺分析網站，主要是透過Python的[Dash套件](https://dash.plotly.com/)製作，資料庫為MySQL。

使用者輸入搜尋工作的關鍵字後，系統會至104人力銀行網站下載搜尋的工作結果，並進行簡單的職缺探索式分析。

[[網站Demo請點此]](http://18.219.72.96:8000/)

![]()

![]()

![]()

## 二、檔案說明

* app
    * index.py： 網站首頁，執行此程式碼部署Dash網站
    * app.py
    * job_analysis_layout.py： 職缺分析頁面版型
    * job_search_layout.py： 職缺搜尋頁面版型
    * callbacks.py： callbacks程式碼
    * custom_functions.py： 客製化函數，包含資料庫連線及104人力銀行爬蟲程式碼
    * assets
        * fonts： 裡面有[Google思源黑體](https://fonts.google.com/specimen/Noto+Sans+TC?preview.text_type=custom)字型檔案，繪製文字雲時會用到
        * jieba_dict： 結巴字典
            * stopdict.txt： 停用詞字典，取自Github專案[tomlinNTUB/Python](https://github.com/tomlinNTUB/Python/blob/master/%E4%B8%AD%E6%96%87%E5%88%86%E8%A9%9E/%E5%81%9C%E7%94%A8%E8%A9%9E.txt)
            * userdict.txt： 自定義字典，取自Github專案[uuboyscy/work104](https://github.com/uuboyscy/work104/blob/master/dict/bigData.txt)
            * custom.css： css，主要加載Google思源黑體字型
    * log： 存放爬蟲程式的執行紀錄
* docker-compose.yml： docker-compose執行檔案
* dockerfile-dash： 部署Dash的docker file設定檔

