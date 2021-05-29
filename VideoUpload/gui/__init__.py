#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目图形用户界面包初始化模块 }
# @Date: 2021/05/29 12:42
import settings
import PySimpleGUI as sg


class BaseWin(object):
    """
    窗口基类
    """

    def __new__(cls, *args, **kwargs):
        sg.change_look_and_feel(settings.GUI_THEMES)
        return super().__new__(cls)

    def __init__(self, title):
        self.title = title
        self.layout = self.init_layout()
        self.window = sg.Window(
            title=self.title,
            layout=self.layout,
            font=settings.WIN_FONT,
            element_padding=settings.ELEMENT_PAD,  # 元素边距
            finalize=True,
        )

    def init_layout(self):
        """
        初始化窗口布局
        :return:
        """
        print('base init layout')
        layout = [
            [sg.InputText('BaseWin')],
        ]
        return layout

    def run(self):
        """运行窗口"""
        self._event_handler()

    def _event_handler(self):
        """
        窗口统一处理事件
        """
        # 开启另一个窗口时,让主窗口不可用,防止用户刻意多次点击造成多个窗口
        # self.window.disable()

        while True:
            event, value_dict = self.window.read()
            print(event, value_dict)

            if event in (sg.WIN_CLOSED,):
                self.quit()
                break

        # 恢复窗口可用
        # self.window.enable()

    def quit(self):
        """退出窗口"""
        self.window.close()
        del self

    def hide(self):
        """隐藏窗口"""
        pass


from .main_win import MainWin
from .category_win import VideoCategoryWin
