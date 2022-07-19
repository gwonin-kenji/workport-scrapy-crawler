# workport-scrapy-crawler

## DB設計リンク

[martデータベース設計](https://www.notion.so/workport-dec2cb8b08df445ea64b4f48ede750c5)

## 環境構築

poetry インストール後 以下実行
```
poetry install
```

envファイルコピー 記入
```
cp .env.sample .env
```

## 収集の流れ

### 会社情報
```
求人一覧ページにアクセス https://www.workport.co.jp/all/search?limit=100&p=1#cnt
↓
求人URL取得
↓
ページングを利用してアクセス https://www.workport.co.jp/all/search?limit=100&p={}#cnt
↓
求人URL取得
↓
求人ページにある会社情報取得
```

### 求人情報
```
求人一覧ページにアクセス https://www.workport.co.jp/all/search?limit=100&p=1#cnt
↓
求人URL取得
↓
ページングを利用してアクセス https://www.workport.co.jp/all/search?limit=100&p={}#cnt
↓
求人URL取得
↓
求人ページにある求人情報取得
```


## ディレクトリ構造

[ディレクトリ構造雛形](https://www.notion.so/Scrapy-951e078b2c4e44a5afdb6bcf70446711)
```
.
├── workport_crawler            : クローラー全体のプロジェクト
│    ├── spiders/
│    │  └── workport_crawler.py : クローラーのロジック記述
│    ├── items.py               : スパイダーが取得するデータを記述
│    ├── middlewares.py         : スパイダーの設定を記述できる(ほとんど触ることはない)
│    ├── models.py              : DBのテーブル定義
│    ├── pipelines.py           : 取得したデータをDBに保存する処理
│    ├── settings.py            : クローラー全体の設定を記述できる
│    ├── identification.py      : 名寄せスクリプト
│    └── utils.py               : utilesモジュール
│
├── README.md 
├── Mikefile                    : 全体の実行処理記述
├── pyproject.toml
├── poetry.lock
├── scrapy.cfg
├── .gitignore
├── .env
├── .env.sample
├── cron_daily.sh               : ec2でのリアルタイム更新実行スクリプト
└── cron_monthly.sh             : ec2での全件更新実行スクリプト
```

## 実行EC2
環境：　sandbox

インスタンス名：　workport

実行場所: /home/ec2-user/workport-scrapy-crawler

## 収集サイト名/リンク
[Workport](https://www.workport.co.jp/)


## 実行方法
### ローカル
```
新規追加
make add_new_company_and_job_offer
```

```
全件更新(求人)
make update_all_job_offers
```

```
全件更新(企業)
make update_all_companies
```

```
名寄せ
make nayose
```
### EC2
```
cronで実行(新規追加＆名寄せ)
workport-scrapy-crawler/cron_daily.sh
```

```
cronで実行(企業＆求人情報 全件更新)
workport-scrapy-crawler/cron_monthly.sh
```

## 実行方法
```
設定しているcron
# 60分おきに実行
*/60 * * * * /bin/bash /home/ec2-user/workport-scrapy-crawler/cron_daily.sh > cron_daily.log 2>&1

# 毎月1日の3時16分に実行
16 3 1 * * /bin/bash /home/ec2-user/workport-scrapy-crawler/cron_monthly.sh > cron_monthly.log 2>&1
```


## 環境変数
| 環境変数名 | 値 |
| ---         |     ---      |
| MART_DB_USER   | 収集データを投入するDBのユーザー名     |
| MART_DB_PASS     | 収集データを投入するDBのパスワード       |
| MART_DB_HOST     | 収集データを投入するDBのホスト名       |
| MART_DB_NAME     | 収集データを投入するDBの名前       |
| MART_DB_PORT     | 収集データを投入するポート番号       |
| SLACK_WEBHOOK_URL     | slack webhook url       |
| NAME_COL_LIST     | 会社名を表すカラム名       |
| DOMAIN_COL_LIST     | ドメインを表すカラム名       |
| PHONE_NUMBER_COL_LIST     | 電話番号を表すカラム名       |
| ADDRESS_COL_LIST     | 住所を表すカラム名       |
| PRESIDENT_COL_LIST     | 代表者を表すカラム名       |
| SINGLE     | default=0       |
| DOUBLE     | default=1       |
| TRIPLE     | default=1       |
| KEY_COL     | default=id       |
