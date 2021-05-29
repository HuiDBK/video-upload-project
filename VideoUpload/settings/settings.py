#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目配置模块 }
# @Date: 2021/05/21 13:10
import os
import yaml
import logging
import coloredlogs
import logging.config

# 项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------- 数据库配置 ---------------------------
# 数据库URI
DB_URI = 'mysql+pymysql://schedule:Schedule123sun@rm-3ns1f77g7856g41371o.mysql.rds.aliyuncs.com:3306/serverdemo'

# --------------------------- 阿里OSS配置 ---------------------------
# 实例名
BUCKET_NAME = 'videoex'

# 地域节点
ENDPOINT = 'oss-cn-hongkong.aliyuncs.com'

# API授权账户
ACCESS_KEY_ID = 'LTAI5t6hDp5XChAmrLDnqtWG'

# 账户密钥
ACCESS_KEY_SECRET = '1j6mVWA5eIJqxfArbFLO8gCbCrTrCi'

# 文件存储目录
OSS_SAVE_DIR = 'video'

# --------------------------- 窗口的基本样式配置 ---------------------------
# 窗口字体
WIN_FONT = ('宋体', 15)

# 菜单项字体
MENU_FONT = ('黑体', 12)

# 元素边距
ELEMENT_PAD = (20, 25)

# 视频文件选择按钮的文件类型
VIDEO_FILE_TYPES = (('ALL Files', '*.mp4'),)

# 字幕文件SRT选择按钮的文件类型
SRT_FILE_TYPES = (('ALL Files', '*.srt'),)

# 窗口主题
GUI_THEMES = 'DarkBlue1'

# 字体突出颜色
FONT_HIGHLIGHT_COLOR = 'red'

# 元素禁止使用时的背景颜色
ELEMENT_DISABLE_BG_COLOR = '#97755C'

# 窗口动态图
WIN_GIF = None

# --------------------------- popup弹窗的基本样式配置 ---------------------------
# 弹窗字体
POPUP_FONT = ('黑体', 13)

# 错误弹窗文本颜色
POPUP_ERROR_COLOR = 'red'

# 通知成功信息弹窗文本颜色
POPUP_SUCCESS_COLOR = '#4881DD'

# --------------------------- 表格采用的样式 ---------------------------
# 表格行高
TAB_ROW_HEIGHT = 30

# 表格单元格默认宽度
TAB_DEF_WIDTH = 15

# 表格对齐方式
TAB_ALIGN = 'center'  # valid values left, right and center

# 表格表头字体
TAB_HEADER_FONT = ('微软雅黑', 13)

# 表格表头背景颜色
TAB_HEADER_BG_COLOR = 'green'

# 表格表头文本颜色
TAB_HEADER_TEXT_COLOR = '#06C7FA'

# --------------------------- tab选项钮采用的样式 ---------------------------
# tab 被选中时的颜色
TAB_SELECTED_COLOR = 'green'

# --------------------------- 项目日志配置 ---------------------------
# 日志配置文件
LOG_CONF_FILE = os.path.join(BASE_DIR, 'settings/logging.yaml')


def setup_logging(default_path=LOG_CONF_FILE, default_level=logging.DEBUG, env_key='LOG_CFG'):
    """
    配置项目日志信息
    :param default_path: 日志文件默认路径
    :param default_level: 日志默认等级
    :param env_key: 系统环境变量名
    :return:
    """
    path = default_path

    value = os.getenv(env_key, None)  # 获取对应的环境变量值
    if value is not None:
        path = value

    if os.path.exists(path):
        with open(path, mode='r', encoding='utf-8') as f:
            try:
                logging_yaml = yaml.safe_load(f.read())
                logging.config.dictConfig(logging_yaml)
                coloredlogs.install(level='DEBUG')
            except Exception as e:
                print(e)
                print('无法加载日志配置文件, 请检查日志目录是否创建, 使用默认的日志配置')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('日志配置文件不存在, 使用默认的日志配置')


def main():
    setup_logging()
    logger = logging.getLogger('server')

    logger.debug('debug log test')
    logger.info('info log test')
    logger.warning('warning log test')
    logger.error('error log test')


if __name__ == '__main__':
    main()
