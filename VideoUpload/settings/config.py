#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 管理配置文件模块 }
# @Date: 2021/05/29 18:14
import os
from utils.yaml_util import ordered_yaml_load
from utils.yaml_util import ordered_yaml_dump

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseConfigManage(object):
    """
    配置文件管理器基类
    """
    config_file = os.path.join(BASE_DIR, 'settings/yaml_conf/account.yaml')
    db_config_node = 'DB_INFO'  # 数据库配置文件的节点名称
    oss_config_node = 'OSS_INFO'  # oss配置文件的节点名称

    def __new__(cls, *args, **kwargs):
        """设置成单例模式"""
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 获取配置文件数据
        self.account_dict = None
        with open(self.config_file, mode='r', encoding='utf-8') as f:
            self.account_dict = ordered_yaml_load(f.read())

    def update(self):
        """
        更新配置文件
        :return:
        """
        with open(self.config_file, mode='w', encoding='utf-8') as f:
            ordered_yaml_dump(self.account_dict, stream=f, allow_unicode=True, default_flow_style=False)


class DBConfigManage(BaseConfigManage):
    """
    数据库配置管理器
    """

    def __init__(self):
        super().__init__()
        self.db_engine = None
        self.db_user = None
        self.db_password = None
        self.db_host = None
        self.db_port = None
        self.db_name = None

        self.__init_db_data()

    def __init_db_data(self):
        """
        初始化数据库配置
        :return:
        """
        db_info = self.account_dict.get(self.db_config_node)
        self.db_engine = db_info.get('db_engine')
        self.db_user = db_info.get('db_user')
        self.db_password = db_info.get('db_password')
        self.db_host = db_info.get('db_host')
        self.db_port = db_info.get('db_port')
        self.db_name = db_info.get('db_name')

    @property
    def db_url(self):
        db_url = f'{self.db_engine}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        return db_url

    def update(self):
        """
        将当前数据库配置信息写入配置文件
        :return:
        """
        db_info = self.account_dict.get(self.db_config_node)
        db_info['db_engine'] = self.db_engine
        db_info['db_user'] = self.db_user
        db_info['db_password'] = self.db_password
        db_info['db_host'] = self.db_host
        db_info['db_port'] = self.db_port
        db_info['db_name'] = self.db_name
        self.account_dict[self.db_config_node] = db_info
        super().update()


class OSSConfigManage(BaseConfigManage):
    """
    对象存储服务配置管理器
    """

    def __init__(self):
        super().__init__()
        self.bucket_name = None
        self.endpoint = None
        self.access_key_id = None
        self.access_key_secret = None
        self.oss_save_dir = None
        self.__init_oss_data()

    def __init_oss_data(self):
        """
        初始化 OSS 服务配置
        :return:
        """
        oss_info = self.account_dict.get(self.oss_config_node)
        self.bucket_name = oss_info.get('bucket_name')
        self.endpoint = oss_info.get('endpoint')
        self.access_key_id = oss_info.get('access_key_id')
        self.access_key_secret = oss_info.get('access_key_secret')
        self.oss_save_dir = oss_info.get('oss_save_dir')

    def update(self):
        """
        将当前 OSS配置信息写入配置文件
        :return:
        """
        oss_info = self.account_dict.get(self.oss_config_node)

        oss_info['bucket_name'] = self.bucket_name
        oss_info['endpoint'] = self.endpoint
        oss_info['access_key_id'] = self.access_key_id
        oss_info['access_key_secret'] = self.access_key_secret
        oss_info['oss_save_dir'] = self.oss_save_dir

        self.account_dict[self.oss_config_node] = oss_info
        super().update()


def main():
    db_config = DBConfigManage()

    print(db_config.db_url)
    db_config.db_name = 'serverdemo'
    db_config.update()
    print(db_config.db_url)

    oss_config = OSSConfigManage()
    oss_config2 = OSSConfigManage()
    oss_config3 = OSSConfigManage()

    print(id(oss_config))
    print(id(oss_config2))
    print(id(oss_config3))

    print(oss_config.oss_save_dir)
    oss_config.oss_save_dir = 'video'
    oss_config.update()
    print(oss_config.oss_save_dir)


if __name__ == '__main__':
    main()
