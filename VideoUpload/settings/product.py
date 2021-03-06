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

# 作者信息
AUTHOR = '忆想不到的晖'
VERSION = 'V1.1.0'
EMAIL = 'huidbk@qq.com'
DESC = '用代码谱写生活，让世界更有趣！！！'
COPYRIGHT = 'CopyRight©2020-2021 编程小灰 ithui.top 赣ICP备20000693号'

# 上传视频信息json文件
UPLOADED_VIDEO_JSON = os.path.join(BASE_DIR, 'logs/uploaded_video.json')


# 上传视频状态类
class UploadStatus:
    """
    上传视频状态类

    0 默认状态

    1 视频正在上传

    2 视频上传到OSS成功、保存数据库失败

    3 视频上传到OSS成功, 保存数据库成功

    4 上传视频到OSS失败
    """

    DEFAULT = 0
    UPLOADING = 1
    UPLOAD_OK_SAVE_FAILED = 2
    UPLOAD_OK_SAVE_SUCCESS = 3
    UPLOAD_FAILED = 4


# --------------------------- 窗口的标题配置 ---------------------------

MAIN_WIN_TITLE = 'OSS上传视频'
CATEGORY_WIN_TITLE = '视频分类管理'
UPLOADED_WIN_TITLE = '上传视频信息'
ACCOUNT_WIN_TITLE = '数据库与OSS管理'

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
# GUI_THEMES = 'Dark'
GUI_THEMES = 'DarkBlue1'
# GUI_THEMES = 'DarkBlue12'

# 字体突出颜色
FONT_HIGHLIGHT_COLOR = 'red'

# 元素禁止使用时的背景颜色, 默认主题颜色
ELEMENT_DISABLE_BG_COLOR = ''

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
LOG_CONF_FILE = os.path.join(BASE_DIR, 'settings/yaml_conf/logging.yaml')


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
