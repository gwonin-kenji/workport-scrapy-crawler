# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from typing import Union, Any

from workport_crawler.items import CompanyItem, RecruitItem
from scrapy import Spider

from workport_crawler.models import (
    LOCAL_URL,
    MART_URL,
    Company,
    JobOffer,
)

from workport_crawler.utils import SlackNotify

from collections import defaultdict
from logging import getLogger
logger = getLogger(__name__)

from icecream import ic


class WorkportCrawlerPipeline:
    def open_spider(self, spider):
        self.DB_URL = LOCAL_URL if spider.test == "ON" else MART_URL
        self.db_company = Company(self.DB_URL)
        self.db_job_offer = JobOffer(self.DB_URL)

        self.slack = SlackNotify()

        self.count_new_company = 0
        self.count_new_job_offer = 0
        self.__companies_list = []
        self.__job_offers_list = []

        # 取得済みの企業/求人のURLをメモリに保存
        self.company_id_dict = defaultdict(bool)
        for id in Company(self.DB_URL).select_company_ids():
            self.company_id_dict[id] = True
        spider.company_id_dict = self.company_id_dict
        
        self.job_offer_id_dict = defaultdict(bool)
        for id in JobOffer(self.DB_URL).select_job_ids():
            self.job_offer_id_dict[id] = True
        spider.job_offer_id_dict = self.job_offer_id_dict


    def process_item(self, item, spider: Spider) -> Union[CompanyItem, RecruitItem]:
        for field in item.fields:
            item.setdefault(field, None)
        record = dict(item)

        if isinstance(item, CompanyItem):
            id = record["company_id"]
            if not self.company_id_dict[id]:
                self.__companies_list.append(record)
                self.count_new_company += 1

        if isinstance(item, RecruitItem):
            id = record["job_id"]
            if not self.job_offer_id_dict[id]: 
                self.__job_offers_list.append(record)
                self.count_new_job_offer += 1
        return item

    def close_spider(self, spider: Spider) -> None:
        logger.info(self.DB_URL)
        self.db_company = Company(self.DB_URL)
        self.db_job_offer = JobOffer(self.DB_URL)
        # 企業情報のdb挿入
        try:
            self.db_company.bulk_insert_mappings(self.__companies_list)
        except Exception as e:
            logger.error(f"会社情報を追加する際にエラーが発生しました。\n{e}")
        # 採用情報のdb挿入
        try:
            self.db_job_offer.bulk_insert_mappings(self.__job_offers_list)
        except Exception as e:
            logger.error(f"採用情報を追加する際にエラーが発生しました。\n{e}")

        # slack通知　新規登録企業数
        self.slack.slack_notify('\n会社情報 【新規追加: {} 件】'.format(self.count_new_company))
        self.slack.slack_notify('\n採用情報 【新規追加: {} 件】'.format(self.count_new_job_offer))


class WorkportUpdatePipeline:
    """
    更新内容のある企業のレコードを更新し
    最終テーブル、過去テーブル、crawledテーブルに保存する
    """
    # NOTE : 企業データは crawled_urlがないのでどう更新するのか。
    # 求人と同時に更新するのか別途で更新するのか
    # 別途で更新する場合は、コードは簡単に書けるけど、収集URLが求人にしかないので二重で収集しないといけなくなる。時間も2倍かかる。
    # 同時に更新する場合は、引数を持たせて企業と求人の更新を分けるので、少しコードが複雑になりそう。


    def open_spider(self, spider):
        self.DB_URL = LOCAL_URL if spider.test == "ON" else MART_URL
        self.db = JobOffer(self.DB_URL)
        self.db_company = Company(self.DB_URL) if spider.company == "ON" else None
        self.target = "企業" if spider.company == "ON" else "求人"

        self.slack: SlackNotify = SlackNotify()

        self.count_updated_amount = 0
        self.updated_data = []
        self.existing_data = self.db.select_all()
        self.existing_comany_data = self.db_company.select_all() if spider.company == "ON" else None
        
        self.start_urls = self.db.select_crawled_urls()
        spider.start_urls = self.start_urls[:100] if spider.test == "ON" else self.start_urls


    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)

        if self.__data_changed(item, spider):
            self.count_updated_amount += 1
            latest_record = dict(item)
            latest_record["id"] = self.__get_data_by_company_id(item)["id"] if spider.company == "ON" else self.__get_data_by_cralwed_url(item)["id"]
            self.updated_data.append(latest_record)

        if len(self.updated_data) == 1000:
            self.db.bulk_update_mappings(self.updated_data)
            self.updated_data = []
        # return item

    def __get_data_by_cralwed_url(self, item) -> dict[str, Any]:
        """DBにもともと存在するデータをcrawled_urlをもとにして取得する。"""
        for data in self.existing_data:
            if data["crawled_url"] == item["crawled_url"]:
                return data

    def __get_data_by_company_id(self, item) -> dict[str, Any]:
        for data in self.existing_comany_data:
            if data["company_id"] == item["company_id"]:
                return data

    def __data_changed(self, item, spider) -> bool:
        """既存のデータに対して変更が合ったかどうかをBOOL値で返す。"""
        if spider.company == "ON":
            ic("企業")
            data = self.__get_data_by_company_id(item)
        else:
            ic("求人")
            data = self.__get_data_by_cralwed_url(item)

        flag = False
        for field in item.fields:
            if data[field] != item[field]:
                if type(data[field]) == list and set(data[field]) == set(item[field]):
                    continue
                flag = True
        return flag

    def close_spider(self, spider: Spider) -> None:
        logger.info(self.DB_URL)
        # データ更新
        if spider.company == "ON":
            self.db_company.bulk_update_mappings(self.updated_data)
        else:
            self.db.bulk_update_mappings(self.updated_data)
        # slack通知　新規登録企業数
        self.slack.slack_notify('\n{}情報 【更新: {} 件】 (全{}件中)'.format(self.target, self.count_updated_amount, len(self.start_urls)))