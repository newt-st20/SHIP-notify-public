#coding: utf-8


from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from assets.database import Base
from datetime import datetime as dt

#データベースのテーブル情報


class Data(Base):
    #テーブルnameの設定,dataというnameに設定
    __tablename__ = "data"
    #Column情報を設定、uniqueはFalseとする（同じ値でも認めるという意味）
    #主キーは行を検索する時に必要、通常は設定しておく
    id = Column(Integer, primary_key=True)
    #nameは投稿者
    name = Column(Text, unique=False)


　　 #articleは投稿内容
article = Column(Text, unique=False)
#timestampは投稿日時
　　 timestamp = Column(DateTime, unique=False)

#初期化する


def __init__(self, name=None, article=None, timestamp=None):
    self.name = name
    self.article = article
    self.timestamp = timestamp
