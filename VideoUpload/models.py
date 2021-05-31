#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目数据库表模型模块 }
# @Date: 2021/05/22 23:14
from settings import DBConfigManage
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, BIGINT, Text, create_engine, ForeignKey

# 创建对象的基类:
Base = declarative_base()

# 初始化数据库连接:
db_engine = create_engine(DBConfigManage().db_url)

# 创建db_session类型:
DBSession = sessionmaker(bind=db_engine, expire_on_commit=False)


class HotFeeds(Base):
    __tablename__ = 'table_hot_feeds'

    id = Column(Integer, autoincrement=True, primary_key=True, comment='主键id')
    item_id = Column(BIGINT, comment='视频唯一id')
    create_time = Column(BIGINT, comment='上传时间')
    item_type = Column(Integer, comment='视频大分类')
    sub_category = Column(Integer, comment='视频子分类')
    video_url = Column(String(255), comment='视频地址')
    sub_url = Column(String(255), comment='srt字幕地址')

    def as_dict(self):
        """
        将对象属性数据转成一个字典
        :return:
        """
        feeds_dict = {
            'id': self.id,
            'item_id': self.item_id,
            'create_time': self.create_time,
            'item_type': self.item_type,
            'sub_category': self.sub_category,
            'video_url': self.video_url,
            'sub_url': self.sub_url
        }
        return feeds_dict


class SubTitle(Base):
    __tablename__ = 'table_subtitle'

    id = Column(Integer, autoincrement=True, primary_key=True, comment='主键id')
    subtitle_id = Column(Integer, comment='子标题id')
    content_eng = Column(Text, comment='英文内容')
    content_ch = Column(Text, comment='中文内容')
    begin_time = Column(String(255), comment='开始时间')
    end_time = Column(String(255), comment='结束时间')
    item_id = Column(BIGINT, comment='视频唯一id')


class VideoCategory(Base):
    """视频大分类模型类"""
    # 表的名字:
    __tablename__ = 'table_category'

    # 表字段结构
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键id')
    category_id = Column(Integer, comment='视频大分类id')
    category_name = Column(String(255), comment='视频大分类名称')

    # 一个大分类对应多个子分类
    sub_categorys = relationship(
        'VideoSubCategory',
        back_populates='video_big_category',
        cascade='all, delete, delete-orphan'
    )

    def __repr__(self):
        return self.category_name


class VideoSubCategory(Base):
    """视频子分类模型类"""

    __tablename__ = 'table_subcategory'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键id')
    subcategory_id = Column(Integer, comment='视频子分类id')
    subcategory_name = Column(String(255), comment='视频子分类名称')

    # 子分类对应的大分类id
    parent_id = Column(Integer, ForeignKey('table_category.category_id'), comment='所属大分类id')

    video_big_category = relationship(
        'VideoCategory',
        back_populates='sub_categorys'
    )

    def __repr__(self):
        return self.subcategory_name


def query_all_category():
    # 创建Session:
    session = DBSession()

    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    video_category = session.query(VideoCategory).filter(VideoCategory.category_id == 1).one()

    print('type:', type(video_category))
    print(f'category_name: {video_category.category_name}')

    # 对应的所有子分类
    sub_categorys = video_category.sub_categorys
    print(len(sub_categorys))
    print(sub_categorys)
    for sub_category in sub_categorys:
        print(sub_category.subcategory_name)

    # 关闭Session:
    session.close()


# def add_user():
#     session = DBSession()
#     user = User(uid=10, username='hui_test', password='123', email='hui@163.com')
#     session.add(user)
#     session.commit()
#     session.close()


def main():
    query_all_category()
    # add_user()


if __name__ == '__main__':
    main()
