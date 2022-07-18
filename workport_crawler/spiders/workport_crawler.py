import scrapy
from scrapy.loader import ItemLoader
from workport_crawler.items import CompanyItem, RecruitItem

from workport_crawler.models import (
    LOCAL_URL,
    MART_URL,
    Company,
    JobOffer,
)

from collections import defaultdict
from icecream import ic

class WorkportSpider(scrapy.Spider):
    name = 'workport_spider'
    custom_settings = {
        "ITEM_PIPELINES": {
           'workport_crawler.pipelines.WorkportCrawlerPipeline': 350,
        }
    }
    allowed_domains = ['workport.co.jp']
    start_urls = ['https://www.workport.co.jp/all/search?limit=100&p=1#cnt']
    page = 1
    page_url = 'https://www.workport.co.jp/all/search?limit=100&p={}#cnt'

    company_ids = defaultdict(bool)
    recruit_ids = defaultdict(bool)


    def parse(self, response):
        recruits = response.css('div.l_main section.recruit h2.mttl a::attr(href)').getall()

        # ページ内に求人がなければ終了
        if len(recruits) == 0:
            return

        # NOTE : 全件収集する場合は以下の条件をコメントアウトする
        if self.page >= 20: #20: 46m 54s #10: 23m
            return
        
        # ページ内の1つ1つの求人に遷移
        for i in recruits:
            yield scrapy.Request(response.urljoin(i), self.get_recruit)
        # 次のページへ遷移
        self.page += 1
        url = self.page_url.format(self.page)
        yield scrapy.Request(url, self.parse)


    def get_recruit(self, response):
        # NOTE: 新規追加 index0に newがあるわけではないので注意
    #     new = response.xpath('//*[@id="SC_ind"]/div[2]/div/div[1]/section[1]/div[1]/ul[1]/li/text()').getall()[0]
    #     if new != "NEW": 
    #         return

        job_id = response.url.strip('/').split('/')[-1]
        company_id = response.url.strip('/').split('/')[-2]

        # NOTE リアルタイム更新は新規記事 or 新規企業を判定する
        if not self.job_offer_id_dict[job_id] and not self.recruit_ids[job_id]:
            ic(self.job_offer_id_dict[job_id])
            ic(job_id)

            self.recruit_ids[job_id] = True

            # recruitItemを作成
            recruit_item = ItemLoader(item=RecruitItem())
            recruit_item.add_value('job_id', job_id)
            recruit_item.add_value('crawled_url', response.url)
            recruit_item.add_value('tags', ','.join(response.css('div.recruitcov ul.condition li::text').getall()))
            recruit_item.add_value('title', response.css('section.recruit h1.mttl::text').get())
            recruit_item.add_value('job_summary', ''.join(response.css('section.jobSummary div.jobSummaryInTop ').getall()))
            for i in response.css('div.jobSummaryIn div.recruitcov2 dl'):
                dt = i.css('dt::text').get()
                dd = '\t'.join(i.css('dd::text').getall())
                recruit_item.add_value(self.return_recruit_key(dt), dd)

            if company_id != 'hikoukai':
                recruit_item.add_value('company_id', company_id)

            yield recruit_item.load_item()

        if not self.company_id_dict[company_id] and not self.company_ids[company_id]:
            print(self.company_id_dict[company_id])
            ic(company_id)

            self.company_ids[company_id] = True

            # companyItemを作成
            if company_id != 'hikoukai':
                company_item = ItemLoader(item=CompanyItem())
                company_item.add_value('company_id', company_id)
                # company_item.add_value('crawled_url', response.url)
                for i in response.css('section.companySummary dl.companySummary-item'):
                    dt = i.css('dt::text').get()
                    dd = '\t'.join(i.css('dd::text').getall())
                    company_item.add_value(self.return_company_key(dt), dd)
            
                yield company_item.load_item()


    def return_recruit_key(self, dt):
        if dt == '職種':
            key = 'job_category'
        elif dt == '応募資格':
            key = 'requirement'
        elif dt == '求めるスキル':
            key = 'required_skills'
        elif dt == '勤務地':
            key = 'location'
        elif dt == '勤務時間':
            key = 'working_hours'
        elif dt == '想定給与':
            key = 'estimated_salary'
        elif dt == '待遇/福利厚生':
            key = 'treatment'
        elif dt == '休日/休暇':
            key = 'holiday'
        elif dt == '雇用形態':
            key = 'employment_status'
        else:
            raise Exception('Unknown recruit_key')
        return key

    def return_company_key(self, dt):
        if dt == '会社名':
            key = 'company_name'
        elif dt == '事業内容':
            key = 'business_details'
        elif dt == '本社所在地':
            key = 'location'
        elif dt == '設立年':
            key = 'establishment_year'
        elif dt == '従業員数':
            key = 'employees'
        elif dt == '資本金':
            key = 'capital'
        elif dt == '売上高':
            key = 'sales'
        elif dt == '平均年齢':
            key = 'average_age'
        else:
            raise Exception('Unknown company_key')
        return key

class WorkportUpdateSpider(WorkportSpider):
    name = 'workport_update_spider'
    custom_settings = {
        "ITEM_PIPELINES": {
           'workport_crawler.pipelines.WorkportUpdatePipeline': 360,
        }
    }
    allowed_domains = ['workport.co.jp']

    def parse(self, response):
        job_id = response.url.strip('/').split('/')[-1]
        company_id = response.url.strip('/').split('/')[-2]

        if self.company == "OFF":
            # recruitItemを作成
            recruit_item = ItemLoader(item=RecruitItem())
            recruit_item.add_value('job_id', job_id)
            recruit_item.add_value('crawled_url', response.url)
            recruit_item.add_value('tags', ','.join(response.css('div.recruitcov ul.condition li::text').getall()))
            recruit_item.add_value('title', response.css('section.recruit h1.mttl::text').get())
            recruit_item.add_value('job_summary', ''.join(response.css('section.jobSummary div.jobSummaryInTop ').getall()))
            for i in response.css('div.jobSummaryIn div.recruitcov2 dl'):
                dt = i.css('dt::text').get()
                dd = '\t'.join(i.css('dd::text').getall())
                recruit_item.add_value(self.return_recruit_key(dt), dd)

            if company_id != 'hikoukai':
                recruit_item.add_value('company_id', company_id)

            yield recruit_item.load_item()

        if self.company == "ON":
            # companyItemを作成
            if company_id != 'hikoukai':
                company_item = ItemLoader(item=CompanyItem())
                company_item.add_value('company_id', company_id)
                # company_item.add_value('crawled_url', response.url)
                for i in response.css('section.companySummary dl.companySummary-item'):
                    dt = i.css('dt::text').get()
                    dd = '\t'.join(i.css('dd::text').getall())
                    company_item.add_value(self.return_company_key(dt), dd)
            
                yield company_item.load_item()
