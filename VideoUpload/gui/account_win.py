#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 阿里OOS、数据库账户管理模块 }
# @Date: 2021/05/29 15:47
import logging
import settings
import pyperclip
from gui import BaseWin
import PySimpleGUI as sg
from settings import DBConfigManage, OSSConfigManage

logger = logging.getLogger('server')


class AccountWin(BaseWin):
    """账户管理窗口"""

    menus = [
        ['窗口跳转', [
            '上传视频窗口::back_main_win',
            '分类管理窗口::back_category_win',
            '查看已上传视频信息::back_uploaded_win']]
    ]

    def __init__(self, title):

        self.password_char = '*'  # 密码隐藏符

        # 数据库与OSS配置管理器
        self.db_config_manage = DBConfigManage()
        self.oss_config_manage = OSSConfigManage()

        # 数据库信息
        self.db_url = self.db_config_manage.db_url
        self.db_user = self.db_config_manage.db_user
        self.db_password = self.db_config_manage.db_password
        self.db_host = self.db_config_manage.db_host
        self.db_port = self.db_config_manage.db_port
        self.db_name = self.db_config_manage.db_name

        # oss信息
        self.bucket_name = self.oss_config_manage.bucket_name  # oss实例
        self.endpoint = self.oss_config_manage.endpoint  # 地域节点
        self.access_key_id = self.oss_config_manage.access_key_id  # 授权ID
        self.access_key_secret = self.oss_config_manage.access_key_secret  # 授权密钥
        self.oss_save_dir = self.oss_config_manage.oss_save_dir  # 保存目录

        super().__init__(title)

    def _create_db_manage_frame(self):
        """
        创建数据库管理布局
        :return: db_manage_frame
        """
        db_manage_frame = [
            [
                sg.Text('数据库地址'),
                sg.Input(default_text=self.db_url, key='db_url', readonly=True, size=(40, 0),
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('复制', key='copy_db_url')
            ],

            [
                sg.Text('数据库主机'),
                sg.Input(default_text=self.db_host, key='db_host', readonly=True, size=(40, 0),
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_db_host')
            ],

            [
                sg.Text('数据库端口'),
                sg.Input(default_text=self.db_port, key='db_port', readonly=True, size=(40, 0),
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_db_port')
            ],

            [
                sg.Text('数据库名称'),
                sg.Input(default_text=self.db_name, key='db_name', readonly=True, size=(40, 0),
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_db_name')
            ],

            [sg.Text('数据库账号')],
            [
                sg.Input(default_text=self.db_user, key='db_user', readonly=True,
                         password_char=self.password_char,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('查看', key='show_db_user'), sg.Button('更改', key='change_db_user')
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
                sg.Text('bucket 实例 '),
                sg.Input(default_text=self.bucket_name, key='oss_bucket', size=(33, 0), readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_oss_bucket')
            ],

            [
                sg.Text('endpoint节点'),
                sg.Input(default_text=self.endpoint, key='oss_endpoint', size=(33, 0), readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_oss_endpoint')
            ],

            [
                sg.Text('OSS 保存目录'),
                sg.Input(default_text=self.oss_save_dir, key='oss_save_dir', size=(33, 0), readonly=True,
                         disabled_readonly_background_color=settings.ELEMENT_DISABLE_BG_COLOR),
                sg.Button('更改', key='change_oss_save_dir')
            ],

            [sg.Text('', pad=(0, 0))],

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
            [sg.Menu(self.menus, font=settings.MENU_FONT)],
            [sg.pin(account_tab_group)]
        ]
        return layout

    # --------------- 显示数据库隐私信息 ---------------
    def _show_db_info(self, key, event):
        """
        根据 key, event 查看数据库相关信息
        :param key: 元素要显示的 key
        :param event: 元素触发的事件
        :return:
        """
        print(key)
        print(event)
        password_char = self.window[key].PasswordCharacter
        if password_char == self.password_char:
            self.window[key].update(password_char='')
            self.window[event].update('隐藏')
        else:
            self.window[key].update(password_char=self.password_char)
            self.window[event].update('查看')

    def show_db_user(self, key, event):
        """
        查看数据库账号
        :return:
        """
        self._show_db_info(key, event)

    def show_db_password(self, key, event):
        """
        查看数据库密码
        :return:
        """
        self._show_db_info(key, event)

    # --------------- 显示OSS隐私信息 ---------------
    def _show_oss_info(self, key, event):
        """
        根据 key, event 查看 OSS 相关信息
        :param key: 元素要显示的 key
        :param event: 元素触发的事件
        :return:
        """
        password_char = self.window[key].PasswordCharacter
        if password_char == self.password_char:
            self.window[key].update(password_char='')
            self.window[event].update('隐藏')
        else:
            self.window[key].update(password_char=self.password_char)
            self.window[event].update('查看')

    def show_oss_access_key_id(self, key, event):
        """
        查看 OSS 授权ID
        :return:
        """
        self._show_oss_info(key, event)

    def show_oss_access_key_secret(self, key, event):
        """
        查看 OSS 授权密钥
        :return:
        """
        self._show_oss_info(key, event)

    # --------------- 更改数据库信息 ---------------
    def _change_db_info(self, key):
        """
        根据 key 改变数据库相关信息
        :param key:
        :return:
        """
        messages = {
            'db_user': '将数据库【账号】更改为: \n',
            'db_password': '将数据库【密码】更改为: \n',
            'db_host': '将数据库【主机地址】更改为: \n',
            'db_port': '将数据库连接【端口】更改为: \n',
            'db_name': '将数据库【名称】更改为: \n'
        }
        msg = messages.get(key)
        db_info = sg.popup_get_text(msg, title='数据库信息更改', font=settings.POPUP_FONT)

        logger.debug(db_info)

        if db_info and db_info is not None:
            # 更新配置文件数据
            if key == 'db_user':
                self.db_user = db_info
                self.db_config_manage.db_user = db_info

            elif key == 'db_password':
                self.db_password = db_info
                self.db_config_manage.db_password = db_info

            elif key == 'db_host':
                self.db_host = db_info
                self.db_config_manage.db_host = db_info

            elif key == 'db_port':
                self.db_port = db_info
                self.db_config_manage.db_port = db_info

            elif key == 'db_name':
                self.db_name = db_info
                self.db_config_manage.db_name = db_info

            # 更新配置文件
            self.db_config_manage.update()
            self.db_url = self.db_config_manage.db_url

            # 更新窗口数据
            self.window[key].update(db_info)
            self.window['db_url'].update(self.db_url)

    def change_db_user(self):
        """
        更改数据库账号
        :return:
        """
        self._change_db_info(key='db_user')

    def change_db_password(self):
        """
        更改数据库密码
        :return:
        """
        self._change_db_info(key='db_password')

    def change_db_host(self):
        """
        更改数据库主机地址
        :return:
        """
        self._change_db_info(key='db_host')

    def change_db_port(self):
        """
        更改数据库主机连接端口
        :return:
        """
        self._change_db_info(key='db_port')

    def change_db_name(self):
        """
        更改数据库名称
        :return:
        """
        self._change_db_info(key='db_name')

    # --------------- 更改OSS信息 ---------------
    def _change_oss_info(self, key):
        """
        根据 key 改变 OSS相关配置信息
        :param key: 要改变的配置选项
        :return:
        """
        messages = {
            'oss_bucket': '将OSS【bucket实例】更改为: \n',
            'oss_endpoint': '将OSS【endpoint节点】更改为: \n',
            'oss_save_dir': '将OSS【保存目录】更改为: \n',
            'access_key_id': '将OSS【授权ID】更改为: \n',
            'access_key_secret': '将OSS【授权密钥】更改为: \n'
        }
        msg = messages.get(key)
        oss_info = sg.popup_get_text(msg, title='OSS信息更改', font=settings.POPUP_FONT)

        logger.debug(oss_info)

        if oss_info and oss_info is not None:
            # 更新配置文件数据
            if key == 'oss_bucket':
                self.bucket_name = oss_info
                self.oss_config_manage.bucket_name = oss_info

            elif key == 'oss_endpoint':
                self.oss_endpoint = oss_info
                self.oss_config_manage.endpoint = oss_info

            elif key == 'oss_save_dir':
                self.oss_save_dir = oss_info
                self.oss_config_manage.oss_save_dir = oss_info

            elif key == 'access_key_id':
                self.access_key_id = oss_info
                self.oss_config_manage.access_key_id = oss_info

            elif key == 'access_key_secret':
                self.access_key_secret = oss_info
                self.oss_config_manage.access_key_secret = oss_info

            # 更新配置文件
            self.oss_config_manage.update()

            # 更新窗口数据
            self.window[key].update(oss_info)

    def change_oss_bucket(self):
        """
        更改 OSS bucket实例名称
        :return:
        """
        self._change_oss_info(key='oss_bucket')

    def change_oss_endpoint(self):
        """
        更改 OSS endpoint地域节点
        :return:
        """
        self._change_oss_info(key='oss_endpoint')

    def change_oss_save_dir(self):
        """
        更改 OSS 保存目录
        :return:
        """
        self._change_oss_info(key='oss_save_dir')

    def change_access_key_id(self):
        """
        更改 OSS 授权ID
        :return:
        """
        self._change_oss_info(key='access_key_id')

    def change_access_key_secret(self):
        """
        更改 OSS 授权密钥
        :return:
        """
        self._change_oss_info(key='access_key_secret')

    def copy_db_url(self):
        """
        复制数据库url地址到剪切板上
        :return:
        """
        db_url = self.window['db_url'].DefaultText
        logger.debug(db_url)
        pyperclip.copy(db_url)

    def _event_handler(self):
        """
        窗口事件监听
        :return:
        """

        # 解决循环引用问题
        from gui import MainWin, VideoCategoryWin, UploadedWin

        while True:
            event, value_dict = self.window.read()
            print(event)
            print(value_dict)

            # 窗口跳转
            if event in (sg.WIN_CLOSED, 'quit') or 'back_main_win' in event:
                self.quit()
                MainWin(title=settings.MAIN_WIN_TITLE).run()
                break
            elif 'back_category_win' in event:
                self.quit()
                VideoCategoryWin(title=settings.CATEGORY_WIN_TITLE).run()
                break
            elif 'back_uploaded_win' in event:
                self.quit()
                UploadedWin(title=settings.UPLOADED_WIN_TITLE).run()
                break

            # 复制数据库地址到剪切板上
            elif event == 'copy_db_url':
                self.copy_db_url()

            # 显示隐私信息
            elif event == 'show_db_user':
                self.show_db_user(key='db_user', event=event)
            elif event == 'show_db_password':
                self.show_db_password(key='db_password', event=event)
            elif event == 'show_access_key_id':
                self.show_oss_access_key_id(key='access_key_id', event=event)
            elif event == 'show_access_key_secret':
                self.show_oss_access_key_secret(key='access_key_secret', event=event)

            # 更新数据库信息
            elif event == 'change_db_user':
                self.change_db_user()
            elif event == 'change_db_password':
                self.change_db_password()
            elif event == 'change_db_host':
                self.change_db_host()
            elif event == 'change_db_port':
                self.change_db_port()
            elif event == 'change_db_name':
                self.change_db_name()

            # 更新OSS信息
            elif event == 'change_oss_bucket':
                self.change_oss_bucket()
            elif event == 'change_oss_endpoint':
                self.change_oss_endpoint()
            elif event == 'change_oss_save_dir':
                self.change_oss_save_dir()
            elif event == 'change_access_key_id':
                self.change_access_key_id()
            elif event == 'change_access_key_secret':
                self.change_access_key_secret()

    def run(self):
        self._event_handler()


def main():
    AccountWin(settings.ACCOUNT_WIN_TITLE).run()


if __name__ == '__main__':
    main()
