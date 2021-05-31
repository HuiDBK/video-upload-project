#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 已上传视频窗口模块 }
# @Date: 2021/05/30 23:18
import time
import json
import settings
from gui import BaseWin
import PySimpleGUI as sg
from models import HotFeeds


class UploadedWin(BaseWin):
    """
    已上传视频窗口类
    """

    # 窗口菜单
    menus = [
        ['窗口跳转', [
            '上传视频窗口::back_main_win',
            '视频分类窗口::back_category_win',
            '账户管理窗口::back_account_win']],
    ]

    def __init__(self, title):
        self.uploaded_video_list = list()

        # 已上传视频表头字段
        self.hot_feeds_cols = [col.comment for col in HotFeeds.__table__.columns]
        self.init_data()
        super().__init__(title)

    def init_data(self):
        """
        初始化已上传视频数据
        :return:
        """
        with open(settings.UPLOADED_VIDEO_JSON, mode='r', encoding='utf-8') as f:
            uploaded_video_json = f.read()

        if uploaded_video_json:
            self.uploaded_video_list = json.loads(uploaded_video_json)

    def init_layout(self):
        """
        初始化已上传视频窗口布局
        :return:
        """
        # 获取已上传视频信息的表格格式数据
        uploaded_video_info = list()
        for uploaded_video_dict in self.uploaded_video_list:
            video_items = list()
            for key, value in uploaded_video_dict.items():
                if key == 'create_time':
                    # 把视频创建时间戳转成具体日期
                    time_local = time.localtime(int(value))
                    value = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
                video_items.append(value)
            uploaded_video_info.append(video_items)

        layout = [
            [sg.Menu(self.menus, font=settings.MENU_FONT)],
            [sg.Text('已上传视频信息如下: ', font=settings.WIN_FONT),
             sg.Button(settings.MAIN_WIN_TITLE, key='main_win_btn'),
             sg.Button(settings.CATEGORY_WIN_TITLE, key='category_win_btn'),
             sg.Button(settings.ACCOUNT_WIN_TITLE, key='account_win_btn')
             ],

            [
                sg.Table(
                    values=uploaded_video_info,
                    headings=self.hot_feeds_cols,
                    header_background_color=settings.TAB_HEADER_BG_COLOR,
                    header_text_color=settings.TAB_HEADER_TEXT_COLOR,
                    enable_events=True,
                    auto_size_columns=False,
                    def_col_width=settings.TAB_DEF_WIDTH,
                    font=settings.TAB_HEADER_FONT,
                    row_height=settings.TAB_ROW_HEIGHT,
                    justification=settings.TAB_ALIGN,
                    key='uploaded_video_table'
                )
            ]
        ]
        return layout

    def _event_handler(self):
        """
        事件监听
        :return:
        """
        from gui import MainWin, VideoCategoryWin, AccountWin

        while True:
            event, value_dict = self.window.read()

            if event in (sg.WIN_CLOSED, 'quit') or 'back_main_win' in event or event == 'main_win_btn':
                self.quit()
                MainWin(title=settings.MAIN_WIN_TITLE).run()
                break
            elif 'back_category_win' in event or event == 'category_win_btn':
                self.quit()
                VideoCategoryWin(title=settings.CATEGORY_WIN_TITLE).run()
                break
            elif 'back_account_win' in event or event == 'account_win_btn':
                self.quit()
                AccountWin(title=settings.ACCOUNT_WIN_TITLE).run()
                break

    def run(self):
        self._event_handler()


def main():
    UploadedWin(settings.UPLOADED_WIN_TITLE).run()


if __name__ == '__main__':
    main()
