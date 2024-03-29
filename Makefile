CMD:=~/.pyenv/shims/poetry run 

# 新規追加
add_new_company_and_job_offer:
	${CMD} scrapy crawl workport_spider -a test=OFF
test_add_new_company_and_job_offer:
	${CMD} scrapy crawl workport_spider -a test=ON

# 名寄せ
nayose:
	${CMD} python workport_crawler/identification.py

#  全件更新(求人)
update_all_job_offers:
	${CMD} scrapy crawl workport_update_spider -a test=OFF -a company=OFF
test_update_all_job_offers:
	${CMD} scrapy crawl workport_update_spider -a test=ON -a company=OFF

#  全件更新(企業)
update_all_companies:
	${CMD} scrapy crawl workport_update_spider -a test=OFF -a company=ON
test_update_all_companies:
	${CMD} scrapy crawl workport_update_spider -a test=ON -a company=ON