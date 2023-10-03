# PLUS LEAGUE 球員數據 API
## 目的
目前 P League 球員數據僅存在官網上，且下載及存取並不方便，
透過爬蟲將前兩季的每場比賽數據抓取到資料庫(第三季官網數據無法存取)，
可提供給想進行分析的使用者方便取用數據的管道

## 專案架構
專案主要分為兩個部分，第一部分是爬蟲，先將資料從官網上爬取下來並存入資料庫；再建立 API 提供使用者存取數據
- 爬蟲
    - 運用 Python 撰寫爬蟲程式碼
    - 運用 RabbitMQ + Celery 開啟多個 Worker 將前兩季的每場數據爬下
    - 將爬下的數據匯入 MySQL 資料庫
![image](https://github.com/joshua881117/p_league_stats/blob/07b88b0e20df970f3c0b56b417ad6c9cfe53caa3/%E6%88%AA%E5%9C%96%202023-10-03%20%E4%B8%8B%E5%8D%8812.09.07.png)

- API
    - 運用 Python 建立 FastAPI
    - API 發送 requests 會到 MySQL 資料庫中拿取特定資料並回傳給使用者
![image](https://github.com/joshua881117/p_league_stats/blob/3693680de02fb142ab4656d123f7c9161ac46fb4/%E6%88%AA%E5%9C%96%202023-10-03%20%E4%B8%8B%E5%8D%8812.09.17.png)

專案中架設的服務(資料庫、爬蟲、API...等)都是用 Docker 建立，並透過 Docker Swarm 管理
![image](https://github.com/joshua881117/p_league_stats/blob/b24fae57aabecbd19cdfcaf3ba7058c798b304b2/%E6%88%AA%E5%9C%96%202023-10-03%20%E4%B8%8B%E5%8D%8812.25.35.png)

建立 CI/CD 流程，當程式碼有變更時，會進行測試、建立映像檔以及自動部署
![image](https://github.com/joshua881117/p_league_stats/blob/b24fae57aabecbd19cdfcaf3ba7058c798b304b2/%E6%88%AA%E5%9C%96%202023-10-03%20%E4%B8%8B%E5%8D%8812.24.31.png)
![image](https://github.com/joshua881117/p_league_stats/blob/b24fae57aabecbd19cdfcaf3ba7058c798b304b2/%E6%88%AA%E5%9C%96%202023-10-03%20%E4%B8%8B%E5%8D%8812.20.36.png)

## 相關網址
- [API](http://172.105.226.173:8889/docs)
  - player_game_stats（球員該場比賽數據）
      - season：賽季，填寫 2020-21 或 2021-22
      - player_name: 球員名稱（例：林志傑）
      - game：賽事編號（例：1）
  -  player_season_stats（球員該賽季整體數據）
      - season：賽季，填寫 2020-21 或 2021-22
      - player_name: 球員名稱（例：林志傑）
      - total_or_avg：累計數據或平均數據，填寫 total 或 avg
      - more_stats：是否要更多數據，填寫 1 或 0
      - advanced_stats：是否要進階數據，填寫 1 或 0
  -  team_season_stats（球隊該賽季整體數據）
      - season：賽季，填寫 2020-21 或 2021-22
      - team_name: 球隊名稱（例：臺北富邦勇士）

## 專案參考書籍
- [Python 大數據專案 X 工程 X 產品 資料工程師的升級攻略](https://www.tenlong.com.tw/products/9786267273739?list_name=b-r7-zh_tw)
