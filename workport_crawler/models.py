import os
from typing import Any, Dict, List

from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select, desc
from sqlalchemy.types import ARRAY, BIGINT, TEXT, TIMESTAMP, Boolean, Integer, Date

load_dotenv()

LOCAL_URL = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}".format(
    drivername="postgresql+psycopg2",
    user=os.getenv("DB_USER"),
    passwd=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port="5432",
    db_name=os.getenv("DB_NAME"),
)

MART_URL = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}".format(
    drivername="postgresql+psycopg2",
    user=os.getenv("MART_DB_USER"),
    passwd=os.getenv("MART_DB_PASS"),
    host=os.getenv("MART_DB_HOST"),
    port="5432",
    db_name=os.getenv("MART_DB_NAME"),
)


Base = declarative_base()


class BaseModel(Base):
    """会社情報テーブルでも、求人情報テーブルでも必要な処理をまとめる。"""

    __abstract__ = True

    def __init__(self, DB_URL: str):
        self._engine = create_engine(DB_URL)
        self._session = Session(bind=self._engine)

    def bulk_insert_mappings(self, records: List[Dict[str, Any]]) -> None:
        self._session.bulk_insert_mappings(
            self.__class__, records, return_defaults=False
        )
        self._session.commit()

    def bulk_update_mappings(self, records: List[Dict[str, Any]]) -> None:
        self._session.bulk_update_mappings(self.__class__, records)
        self._session.commit()

    def select_all(self):
        res = list()
        records = self._session.query(self.__class__).all()
        for record in records:
            res.append(record.__dict__)
        return res

    def select_company_ids(self) -> set:
        company_ids = set()
        results = self._session.execute(select(self.__class__.company_id))
        self._session.commit()
        for result in results:
            company_ids.add(result.company_id)
        return company_ids

    def recreate_table(self) -> None:
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    def select_crawled_urls(self) -> List:
        results = self._session.execute(select(self.__class__.crawled_url))
        crawled_urls = [result.crawled_url for result in results]
        return crawled_urls

class Company(BaseModel):
    __tablename__ = 'workport_company'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    company_id = Column(TEXT, unique=True, comment="企業ID")
    # crawled_url = Column(TEXT, comment="収集元URL")
    corporate_number = Column(BIGINT, nullable=True, comment="法人番号")
    company_name = Column(TEXT, comment="会社名")
    business_details = Column(TEXT, comment="事業内容")
    location = Column(TEXT, comment="本社所在地")
    establishment_year = Column(TEXT, comment="設立年")
    employees = Column(TEXT, comment="従業員数")
    capital = Column(TEXT, comment="資本金")
    sales = Column(TEXT, comment="売上高")
    average_age = Column(TEXT, comment="平均年齢")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )


class JobOffer(BaseModel):
    __tablename__ = 'workport_jobs'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    job_id = Column(TEXT, unique=True, comment="求人ID")
    crawled_url = Column(TEXT, comment="収集元URL")
    tags = Column(TEXT, comment="求人タグ")
    title = Column(TEXT, comment="求人タイトル")
    job_summary = Column(TEXT, comment="求人概要")
    job_category = Column(TEXT, comment="職種")
    requirement = Column(TEXT, comment="応募資格")
    required_skills = Column(TEXT, comment="求めるスキル")
    location = Column(TEXT, comment="勤務地")
    working_hours = Column(TEXT, comment="勤務時間")
    estimated_salary = Column(TEXT, comment="想定給与")
    treatment = Column(TEXT, comment="待遇・福利厚生")
    holiday = Column(TEXT, comment="休日・休暇")
    employment_status = Column(TEXT, comment="雇用形態")
    is_open = Column(Boolean, default=True, comment="求人公開有無")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    company_id = Column(
        TEXT, 
        ForeignKey(
            'workport_company.company_id',
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    def select_job_ids(self) -> set:
        job_ids = set()
        results = self._session.execute(select(self.__class__.job_id))
        self._session.commit()
        for result in results:
            job_ids.add(result.job_id)
        return job_ids