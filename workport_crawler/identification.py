"""
multiprocessingを使用した高速な名寄せ
"""
from typing import Any
from crawler_utils.db import DBAdapter, BASE
from sqlalchemy import (
    TEXT,
    Integer,
    Column,
    TIMESTAMP,
    func
)
from identipy import IdentipyV2
import pathlib 
import sys
from identipy.utils.logger import log

import datetime


"""
.envの中身 sample

NAME_COL_LIST = company_name
DOMAIN_COL_LIST = company_url
PHONE_NUMBER_COL_LIST = phone_number
ADDRESS_COL_LIST = location
PRESIDENT_COL_LIST = representative_name
SINGLE = 0
DOUBLE = 1
TRIPLE = 1

KEY_COL = id
"""

ENV_PATH = pathlib.Path().cwd()
print(ENV_PATH)

# TODO : 本番とテストを引数で指定して分ける

# mart_adapter = DBAdapter(  # nosec
#     dotenv_path=f"{ENV_PATH}/.env",
#     env_db_host="MART_DB_HOST",  # DB_HOST # SD_DB_HOST # MART_DB_HOST
#     env_db_name="MART_DB_NAME",  # DB_NAME # SD_DB_NAME # MART_DB_NAME
#     env_db_user="MART_DB_USER",  # DB_USER # SD_DB_USER # MART_DB_USER
#     env_db_pass="MART_DB_PASS",  # DB_PASS # SD_DB_PASS # MART_DB_PASS
#     db_type="postgresql",
# )

mart_adapter = DBAdapter(  # nosec
    dotenv_path=f"{ENV_PATH}/.env",
    env_db_host="DB_HOST",  # DB_HOST # SD_DB_HOST # MART_DB_HOST
    env_db_name="DB_NAME",  # DB_NAME # SD_DB_NAME # MART_DB_NAME
    env_db_user="DB_USER",  # DB_USER # SD_DB_USER # MART_DB_USER
    env_db_pass="DB_PASS",  # DB_PASS # SD_DB_PASS # MART_DB_PASS
    db_type="postgresql",
)

class DBStartupCompanies(BASE):
    """
    workport_company の DB操作を行うクラス
    """

    __tablename__ = "workport_company"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(TEXT, nullable=False)
    corporate_number = Column(Integer)
    company_name = Column(TEXT)
    location = Column(TEXT)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


    def update_records(self, company_list: list[dict[str, Any]]) -> None:
        """
        レコードをまとめて一括update
        """
        mart_adapter.session.bulk_update_mappings(DBStartupCompanies, company_list)
        mart_adapter.session.commit()

    def select_added_new_data(self) -> dict:
        """
        今日の日付で追加されたデータを抽出
        """
        today = datetime.datetime.today().date()
        res = mart_adapter.session.query(DBStartupCompanies).filter(func.DATE(DBStartupCompanies.created_at) == today, DBStartupCompanies.corporate_number == None).all()
        return dict(zip([r.id for r in res], [r for r in res]))


if __name__ == "__main__":

    identipy = IdentipyV2(dotenv_path=f'{ENV_PATH}/.env')
    data = DBStartupCompanies().select_added_new_data()
    log.info("新規追加分の名寄せ開始")
    log.info(f"全 {len(data)}件の新規企業を名寄せします")

    if len(data):
        update_data = identipy.run([data[key].__dict__ for key in data])
        update_list = []
        for update in update_data:
            company = data[update['id']]
            company.corporate_number = int(update['corporate_number'])
            update_list.append(vars(company))
        DBStartupCompanies().update_records(update_list)
    else:
        log.info("名寄せするデータがありません")