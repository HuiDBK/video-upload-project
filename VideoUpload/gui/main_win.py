#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 主窗口模块 }
# @Date: 2021/05/29 12:47
import os
import uuid
import utils
import logging
import settings
import threading
from gui import BaseWin
import PySimpleGUI as sg
from pysubs2 import SSAFile
from settings import OSSConfigManage
from datetime import datetime, timedelta
from sqlalchemy.exc import DatabaseError
from gui.category_win import VideoCategoryWin
from models import DBSession, VideoCategory, HotFeeds, SubTitle

logger = logging.getLogger('server')


class MainWin(BaseWin):
    """主窗口, 起始窗口"""

    # 菜单项
    menus = [
        ['已上传视频信息', [
            '查看上传视频信息::show_video_info']],

        ['视频分类设置', [
            '添加视频分类::add_video_category',
            '删除视频分类::del_video_category']],

        ['帮助', [
            '关于作者::about_author']],
    ]

    # 元素边距
    lr_tuple = (15, 15)  # 左右边距
    ud_tuple = (30, 30)  # 上下边距
    el_pad_tuple = (lr_tuple, ud_tuple)

    # 字体突出颜色
    highlight_color = settings.FONT_HIGHLIGHT_COLOR

    def __init__(self, title):
        self.current_category = None  # 当前视频分类
        self.all_video_category = None
        self.sub_categorys = None  # 当前分类对应的所有子分类

        # 上传标记
        # 0默认
        # 1正在上传视频
        # 2上传视频失败
        # 3视频信息保存数据库失败
        # 4上传视频成功并成功保存到了数据库
        self.upload_flag = 0

        self.init_data()
        super().__init__(title)
        # self.window.ElementPadding = self.el_pad_tuple

    def init_data(self):
        """
        初始化界面数据
        :return:
        """
        # 从数据库中获取所有视频大分类
        session = DBSession()
        all_video_category = session.query(VideoCategory).all()
        self.all_video_category = all_video_category

        # 设置默认分类
        if len(all_video_category) > 0:
            self.current_category = all_video_category[0]

        # 根据视频默认分类获取其所有子分类
        self.sub_categorys = self.current_category.sub_categorys
        session.close()

    def add_video_category(self):
        """
        添加视频分类
        :return:
        """
        print('添加视频分类')
        self.quit()
        category_win = VideoCategoryWin('category')
        category_win.run()

    def del_video_category(self):
        """
        删除视频分类
        :return:
        """
        self.add_video_category()

    def init_layout(self):
        """初始化窗口布局"""

        layout = [
            [sg.Menu(self.menus, key='menus', size=(8, 2), font=settings.MENU_FONT)],
            [sg.Text('请选择你要上传的'),
             sg.Text('视频', text_color=self.highlight_color),
             sg.Text('和'),
             sg.Text('字幕SRT', text_color=self.highlight_color),
             sg.Text('文件')
             ],
            [
                sg.Text('视频文件'), sg.InputText(key='input_video'),
                sg.FileBrowse('选择', key='video', file_types=settings.VIDEO_FILE_TYPES)
            ],
            [
                sg.Text('字幕文件'), sg.InputText(key='input_srt'),
                sg.FileBrowse('选择', key='srt', file_types=settings.SRT_FILE_TYPES)
            ],
            [
                sg.Text('视频大类'),
                sg.Combo(
                    self.all_video_category,
                    default_value=self.current_category, size=(12, 0),
                    key='video_big_category',
                    enable_events=True, readonly=True,
                ),
                sg.Text(),
                sg.Text('视频子类'),
                sg.Combo(
                    self.sub_categorys, size=(12, 0),
                    key='video_subcategory',
                    auto_size_text=False, readonly=True
                )
            ],
            [sg.Cancel('重 置', key='reset'), sg.Submit('上 传', key='upload')],
        ]
        return layout

    def run(self):
        """开启窗口"""
        # 启用协程开启事件监听
        self._event_handler()
        logger.debug('close win')

    def reset_info(self):
        """
        重置窗口信息
        :return:
        """
        self.window['input_video'].update('')
        self.window['input_srt'].update('')
        self.window['video_big_category'].update('')
        self.window['video_subcategory'].update('')

    def upload_video_info(self, value_dict: dict):
        """
        上传视频信息到阿里OSS
        :param value_dict: 视频信息字典
        :return:
        """
        logger.debug(value_dict)
        video_path = value_dict.get('input_video')
        srt_path = value_dict.get('input_srt')
        video_big_category = value_dict.get('video_big_category')
        video_subcategory = value_dict.get('video_subcategory')

        # 校验参数
        video_info_list = [video_path, srt_path, video_big_category, video_subcategory]
        if not all(video_info_list):
            logger.debug('参数不完整')
            sg.popup('请把视频上传信息填写完整\n', title='参数不完整', font=settings.POPUP_FONT)
            return

        if not os.path.exists(video_path):
            msg = '视频文件路径错误, 文件不存在!!!\n'
            sg.popup(msg, title='文件不存在', font=settings.POPUP_FONT)
            return

        if not os.path.exists(srt_path):
            msg = 'srt字幕文件路径错误, 文件不存在!!!\n'
            sg.popup(msg, title='文件不存在', font=settings.POPUP_FONT)
            return

        # 获取srt字幕信息
        with open(srt_path, mode='r', encoding='utf-8') as f:
            srt_content = f.read()

        if not srt_content:
            msg = f'srt字幕文件: {srt_path},空内容'
            logger.info(msg)
            sg.popup(msg + '\n', title='空文件', font=settings.POPUP_FONT)
            return

        logger.debug('有效参数')
        logger.debug('开启线程上传视频')
        # 标记正在上传视频
        self.upload_flag = 1
        self.window.disable()
        params = [video_path, srt_path, video_big_category, video_subcategory]
        upload_thread = threading.Thread(target=self._upload_video_info, args=params)
        upload_thread.start()

    def _upload_video_info(self, video_path, srt_path, video_big_category, video_subcategory):
        """
        上传视频信息到阿里OSS并保存到数据库
        :param video_path: 视频路径
        :param srt_path: 字幕文件路径
        :param video_big_category: 视频大分类
        :param video_subcategory: 视频子分类
        :return:
        """

        # 把视频存储到阿里OSS中
        video_item_id = str(uuid.uuid1())  # 生成视频唯一id
        video_save_name = video_item_id + '.mp4'
        srt_save_name = video_item_id + '.srt'
        oss_save_dir = OSSConfigManage().oss_save_dir

        video_save_path = oss_save_dir + '/' + video_save_name
        srt_save_path = oss_save_dir + '/' + srt_save_name

        try:
            video_url = utils.oss_server.put_obj_from_file(video_save_path, video_path)
            srt_url = utils.oss_server.put_obj_from_file(srt_save_path, srt_path)
        except Exception as e:
            self.upload_flag = 2  # 标记上传失败
            logger.error(e)
            return

        logger.info(f'video_url -> {video_url}')
        logger.info(f'srt_url -> {srt_url}')

        # 提取srt字幕相关数据
        subs = SSAFile.load(srt_path, encoding='utf-8')

        # 保存到数据库中
        with DBSession() as session:
            try:
                # 保存视频信息到数据库
                hot_feeds = HotFeeds(
                    item_id=video_item_id,
                    item_type=video_big_category.category_id,
                    sub_category=video_subcategory.subcategory_id,
                    video_url=video_url,
                    sub_url=srt_url
                )
                session.add(hot_feeds)

                # a = 1 / 0

                # 保存字幕信息到数据库
                for subtitle_id, sub in enumerate(subs):
                    start = sub.start  # 字幕开始时间，单位毫秒
                    begin_time = datetime.fromtimestamp(start / 1000) - timedelta(hours=8)
                    begin_time = begin_time.strftime("%H:%M:%S,%f")[:-3]

                    end = sub.end  # 字幕结束时间
                    end_time = datetime.fromtimestamp(end / 1000) - timedelta(hours=8)
                    end_time = end_time.strftime("%H:%M:%S,%f")[:-3]
                    plaintexts = sub.plaintext.split('\n')  # 纯文本
                    content_eng = plaintexts[0]
                    content_ch = plaintexts[1]

                    logger.debug(subtitle_id)
                    logger.debug(begin_time)
                    logger.debug(end_time)
                    logger.debug(content_eng)
                    logger.debug(content_ch)

                    subtitle_id = subtitle_id + 1
                    sub_title = SubTitle(
                        subtitle_id=subtitle_id,
                        content_eng=content_eng,
                        content_ch=content_ch,
                        begin_time=begin_time,
                        end_time=end_time,
                        item_id=video_item_id
                    )
                    session.add(sub_title)
            except (Exception, DatabaseError) as e:
                self.upload_flag = 3  # 保存数据库失败
                session.rollback()
                logger.error(e)
                return
            else:
                self.upload_flag = 4  # 标记上传成功并成功保存数据
                session.commit()
        msg = f'上传视频成功, ' \
              f'所属大类 -> {video_big_category}' \
              f'所属子类 -> {video_subcategory}'
        logger.info(msg)
        self.reset_info()

    def update_subcategory(self, value_dict):
        """
        更新子分类
        :return:
        """
        video_category = value_dict.get('video_big_category')

        # 如果与当前分类不一致，则更新子分类
        if video_category.category_name != self.current_category.category_name:
            print('切换大分类，更新对应的子分类')
            self.current_category = video_category
            session = DBSession()
            session.add(video_category)
            self.sub_categorys = video_category.sub_categorys
            session.close()
            if len(self.sub_categorys) == 0:
                self.sub_categorys = ['暂无分类']
            self.window['video_subcategory'].update(values=self.sub_categorys)

    def _check_upload_status(self):
        """
        检测上传视频状态
        :return:
        """
        if self.upload_flag in (2, 3, 4):
            sg.popup_animated(image_source=None)  # 关闭等待动画
            self.window.enable()

        if self.upload_flag == 1:
            # 正在上传视频
            sg.popup_animated(image_source=sg.DEFAULT_BASE64_LOADING_GIF, message='上传视频中...')

        elif self.upload_flag == 2:
            # 上传失败
            self.upload_flag = 0
            msg = '上传视频、字幕srt文件到阿里OSS失败\n'
            sg.popup_error(msg, title='上传失败', text_color=settings.POPUP_ERROR_COLOR, font=settings.POPUP_FONT)

        elif self.upload_flag == 3:
            # 上传视频成功, 但保存数据库失败
            self.upload_flag = 0
            msg = '保存视频信息到数据库失败！！！\n'
            sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)

        elif self.upload_flag == 4:
            # 上传成功并成功保存到数据库中
            self.upload_flag = 0
            msg = '上传视频信息到阿里OSS成功, 并成功保存数据\n'
            sg.popup(msg, title='上传视频成功', font=settings.POPUP_FONT, text_color=settings.POPUP_SUCCESS_COLOR)

    def _event_handler(self):
        """
        窗口事件监听
        """

        while True:
            event, value_dict = self.window.read(timeout=10)
            # logger.debug(event)
            # logger.debug(value_dict)

            self._check_upload_status()

            # 事件处理
            if event in (sg.WIN_CLOSED,):
                self.quit()
                break
            elif event == 'reset':
                self.reset_info()
            elif event == 'upload':
                self.upload_video_info(value_dict)
            elif event == 'video_big_category':
                self.update_subcategory(value_dict)  # 切换大分类更新对应的子分类
            elif 'add_video_category' in event:
                self.add_video_category()
            elif 'del_video_category' in event:
                self.del_video_category()


def main():
    MainWin('main').run()


if __name__ == '__main__':
    main()
