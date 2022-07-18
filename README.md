# workport-scrapy-crawler

# workport_crawler

workportから会社と採用データを収集するクローラー

## 環境構築
- パッケージのインストール
```
poetry install
```
- .env作成
```
cp .env.sample .env
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

## 実行
- リアルタイム更新（新規追加）
```
make add_new_company_and_job_offer
```
- 名寄せ
```
make nayose
```
- 全件更新(求人)
```
make update_all_job_offers
```
- 全件更新(企業)
```
make update_all_companies
```