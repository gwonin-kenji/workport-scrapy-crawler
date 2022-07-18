# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
import re


def preprocessing(value):
    value = re.sub('(\r|\t|\n|\u3000)', '', value)
    return value

def preprocess_text(text):
    return bytes(re.sub(' +', ' ', text.strip().replace('\t', ' ').replace("\u3000", ' ').replace('\xa0', ' ')\
        .replace('\n', ' ').replace('\r', ' ').replace('<br/>', ' ').replace('\\', '\\\\')), 'utf-8').decode('utf-8', 'ignore')


class CompanyItem(Item):
    company_id = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 企業id
    # crawled_url = Field(
    #     input_processor=MapCompose(remove_tags), 
    #     output_processor=TakeFirst()
    #     ) # 収集元URL
    company_name = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 会社名
    business_details = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 事業内容
    location = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 本社所在地
    establishment_year = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 設立年
    employees = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 従業員数
    capital = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 資本金
    sales = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 売上高
    average_age = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 平均年齢

class RecruitItem(Item):
    job_id = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 求人ID
    crawled_url = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 収集元URL
    tags = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 求人タグ
    title = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 求人タイトル
    job_summary = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 求人概要
    job_category = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 職種
    requirement = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 応募資格
    required_skills = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 求めるスキル
    location = Field(
        input_processor=MapCompose(remove_tags, preprocess_text),
        output_processor=TakeFirst()
        ) # 勤務地
    working_hours = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 勤務時間
    estimated_salary = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 想定給与
    treatment = Field(
        input_processor=MapCompose(remove_tags, preprocess_text), 
        output_processor=TakeFirst()
        ) # 待遇・福利厚生
    holiday = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 休日・休暇
    employment_status = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 雇用形態
    company_id = Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst()
        ) # 企業id

