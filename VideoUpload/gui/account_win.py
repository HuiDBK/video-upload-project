#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 阿里OOS、数据库账户管理模块 }
# @Date: 2021/05/29 15:47
import logging
import settings
from gui import BaseWin
import PySimpleGUI as sg
from settings import DBConfigManage, OSSConfigManage

logger = logging.getLogger('server')


class AccountWin(BaseWin):

    def __init__(self, title):

        self.password_char = '*'  # 密码隐藏符

        # 数据库与OSS配置管理器
        self.db_config_manage = DBConfigManage()
        self.oss_config_manage = OSSConfigManage()

        # 数据库信息
        self.db_user = self.db_config_manage.db_user
        self.db_password = self.db_config_manage.db_password
        self.db_url = self.db_config_manage.db_url

        # oss信息
        self.bucket_name = self.oss_config_manage.bucket_name  # oss实例
        self.endpoint = self.oss_config_manage.endpoint  # 地域节点
        self.access_key_id = self.oss_config_manage.access_key_id  # 授权ID
        self.access_key_secret = self.oss_config_manage.access_key_secret  # 授权密钥

        super().__init__(title)

    def _create_db_manage_frame(self):
        """
        创建数据库管理布局
        :return: db_manage_frame
        """
        db_manage_frame = [
            [sg.Text('数据库地址')],
            [
                sg.Input(default_text=self.db_url, key='db_url', readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_db_url')
            ],

            [sg.Text('数据库账号')],
            [
                sg.Input(default_text=self.db_user, key='db_user', readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_db_user')
            ],

            [sg.Text('数据库密码')],
            [
                sg.Input(default_text=self.db_password, password_char=self.password_char,
                         key='db_password', readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('查看', key='show_db_password'), sg.Button('更改', key='change_db_password')
            ]
        ]
        return db_manage_frame

    def _create_oss_manage_frame(self):
        """
        创建对象存储服务管理布局
        :return: oss_manage_frame
        """
        oss_manage_frame = [
            [
                sg.Text('OSS 实例'),
                sg.Input(default_text=self.bucket_name, key='oss_bucket', size=(33, 0), readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_oss_bucket')
            ],

            [
                sg.Text('地域节点'),
                sg.Input(default_text=self.endpoint, key='oss_endpoint', size=(33, 0), readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_oss_endpoint')
            ],

            [sg.Text('授权ID')],
            [
                sg.Input(default_text=self.access_key_id, key='access_key_id',
                         password_char=self.password_char, readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('查看', key='show_access_key_id'), sg.Button('更改', key='change_access_key_id')
            ],

            [sg.Text('授权密钥')],
            [
                sg.Input(default_text=self.access_key_secret, key='access_key_secret',
                         password_char=self.password_char, readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('查看', key='show_access_key_secret'), sg.Button('更改', key='change_access_key_secret')
            ]
        ]
        return oss_manage_frame

    def init_layout(self):
        """
        初始化账户管理窗口布局
        :return:
        """
        db_manage_frame = self._create_db_manage_frame()
        oss_manage_frame = self._create_oss_manage_frame()

        db_manage_tab = sg.Tab(
            title='数据库管理',
            key='db_manage_tab',
            layout=[[sg.Column(db_manage_frame)]]
        )

        oss_manage_tab = sg.Tab(
            title='OSS管理',
            key='oss_manage_tab',
            layout=[[sg.Column(oss_manage_frame)]]
        )

        account_tab_group = sg.TabGroup(
            [[db_manage_tab, oss_manage_tab]],
            key='account_tab_group',
            enable_events=True,
            selected_background_color=settings.TAB_SELECTED_COLOR
        )
        layout = [
            [sg.pin(account_tab_group)]
        ]
        return layout

    def _show_db_password(self):
        """
        查看数据库密码
        :return:
        """
        password_char = self.window['db_password'].PasswordCharacter
        if password_char == self.password_char:
            self.window['db_password'].update(password_char='')
            self.window['show_db_password'].update('隐藏')
        else:
            self.window['db_password'].update(password_char=self.password_char)
            self.window['show_db_password'].update('查看')

    def _show_oss_access_key_id(self):
        """
        查看 OSS 授权ID
        :return:
        """
        password_char = self.window['access_key_id'].PasswordCharacter
        if password_char == self.password_char:
            self.window['access_key_id'].update(password_char='')
            self.window['show_access_key_id'].update('隐藏')
        else:
            self.window['access_key_id'].update(password_char=self.password_char)
            self.window['show_access_key_id'].update('查看')

    def _show_oss_access_key_secret(self):
        """
        查看 OSS 授权密钥
        :return:
        """
        password_char = self.window['access_key_secret'].PasswordCharacter
        if password_char == self.password_char:
            self.window['access_key_secret'].update(password_char='')
            self.window['show_access_key_secret'].update('隐藏')
        else:
            self.window['access_key_secret'].update(password_char=self.password_char)
            self.window['show_access_key_secret'].update('查看')

    def _change_db_user(self):
        """
        改变数据库账号
        :return:
        """
        db_user = sg.popup_get_text('请输入您要更改的数据库账号\n', font=settings.POPUP_FONT)

        logger.debug(db_user)

        if db_user and db_user is not None:
            # 更新配置文件数据
            self.db_user = db_user
            self.db_config_manage.db_user = db_user
            self.db_config_manage.update()
            self.db_url = self.db_config_manage.db_url

            # 更新窗口数据
            self.window['db_user'].update(self.db_user)
            self.window['db_url'].update(self.db_url)

    def _change_db_password(self):
        """
        改变数据库密码
        :return:
        """
        db_password = sg.popup_get_text('请输入您要更改的数据库密码\n', font=settings.POPUP_FONT)

        logger.debug(db_password)

        if db_password and db_password is not None:
            # 更新配置文件数据
            self.db_password = db_password
            self.db_config_manage.db_password = db_password
            self.db_config_manage.update()
            self.db_url = self.db_config_manage.db_url

            # 更新窗口数据
            self.window['db_password'].update(self.db_password)
            self.window['db_url'].update(self.db_url)

    def _change_oss_bucket(self):
        """
        改变 OSS 实例名称
        :return:
        """
        oss_bucket = sg.popup_get_text('请输入您要更改的Bucket实例名\n', font=settings.POPUP_FONT)

        logger.debug(oss_bucket)

        if oss_bucket and oss_bucket is not None:
            # 更新配置文件数据
            self.oss_bucket = oss_bucket
            self.oss_config_manage.bucket_name = oss_bucket
            self.oss_config_manage.update()

            # 更新窗口数据
            self.window['oss_bucket'].update(self.oss_bucket)

    def _change_oss_endpoint(self):
        """
        改变 OSS 地域节点
        :return:
        """
        oss_endpoint = sg.popup_get_text('请输入您要更改的地域节点信息\n', font=settings.POPUP_FONT)

        logger.debug(oss_endpoint)

        if oss_endpoint and oss_endpoint is not None:
            # 更新配置文件数据
            self.oss_endpoint = oss_endpoint
            self.oss_config_manage.endpoint = oss_endpoint
            self.oss_config_manage.update()

            # 更新窗口数据
            self.window['oss_endpoint'].update(self.oss_endpoint)

    def _change_access_key_id(self):
        """
        改变授权id
        :return:
        """
        access_key_id = sg.popup_get_text('请输入您要更改的授权ID\n', font=settings.POPUP_FONT)

        logger.debug(access_key_id)

        if access_key_id and access_key_id is not None:
            # 更新配置文件数据
            self.access_key_id = access_key_id
            self.oss_config_manage.access_key_id = access_key_id
            self.oss_config_manage.update()

            # 更新窗口数据
            self.window['access_key_id'].update(self.access_key_id)

    def _change_access_key_secret(self):
        """
        改变 OSS 密钥
        :return:
        """
        access_key_secret = sg.popup_get_text('请输入您要更改的授权密钥\n', font=settings.POPUP_FONT)

        logger.debug(access_key_secret)

        if access_key_secret and access_key_secret is not None:
            # 更新配置文件数据
            self.access_key_secret = access_key_secret
            self.oss_config_manage.access_key_secret = access_key_secret
            self.oss_config_manage.update()

            # 更新窗口数据
            self.window['access_key_secret'].update(self.access_key_secret)

    def _event_handler(self):
        """
        窗口事件监听
        :return:
        """
        while True:
            event, value_dict = self.window.read()
            print(event)
            print(value_dict)

            # 事件监听
            if event in (sg.WIN_CLOSED, 'quit'):
                self.quit()
                break
            elif event == 'show_db_password':
                self._show_db_password()
            elif event == 'show_access_key_id':
                self._show_oss_access_key_id()
            elif event == 'show_access_key_secret':
                self._show_oss_access_key_secret()

            # 更新数据库信息
            elif event == 'change_db_user':
                self._change_db_user()
            elif event == 'change_db_password':
                self._change_db_password()

            # 更新OSS信息
            elif event == 'change_oss_bucket':
                self._change_oss_bucket()
            elif event == 'change_oss_endpoint':
                self._change_oss_endpoint()
            elif event == 'change_access_key_id':
                self._change_access_key_id()
            elif event == 'change_access_key_secret':
                self._change_access_key_secret()

    def run(self):
        self._event_handler()


def main():
    AccountWin('account').run()


if __name__ == '__main__':
    main()
