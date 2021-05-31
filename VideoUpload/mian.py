#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目主入口模块 }
# @Date: 2021/05/21 13:04
import settings
from gui import MainWin


def main():
    settings.setup_logging()
    MainWin(settings.MAIN_WIN_TITLE).run()


if __name__ == '__main__':
    main()
