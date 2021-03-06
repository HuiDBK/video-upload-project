#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 主窗口模块 }
# @Date: 2021/05/29 12:47
import os
import time
import json
import utils
import random
import logging
import settings
import threading
import PySimpleGUI as sg
from pysubs2 import SSAFile
from settings import UploadStatus
from settings import OSSConfigManage
from datetime import datetime, timedelta
from sqlalchemy.exc import DatabaseError
from models import DBSession, VideoCategory, HotFeeds, SubTitle, VideoSubCategory
from gui import BaseWin, VideoCategoryWin, AccountWin, UploadedWin

logger = logging.getLogger('server')


class MainWin(BaseWin):
    """主窗口, 起始窗口"""

    # 菜单项
    menus = [
        ['上传视频信息', [
            '查看上传视频信息::show_uploaded_video',
            '查看保存数据库失败信息::show_save_failed_video']],

        ['视频分类设置', [
            '添加视频分类::add_video_category',
            '删除视频分类::del_video_category']],

        ['账户管理', [
            '数据库账户管理::db_account_manage',
            'OSS 账户管理::oss_account_manage']],

        ['帮助', [
            '版本信息::about_author']],
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

        # 上传进度
        self.upload_rate = 0
        self.current_progress = 1  # 记录当前进度
        self.total_value = 10000  # 记录总进度大小

        self.upload_error = None  # 记录上传时出现的错误

        self.uploaded_video_list = list()  # 已上传视频列表

        # 上传视频状态
        self.upload_status = UploadStatus.DEFAULT

        self.init_data()
        super().__init__(title)

    def init_data(self):
        """
        初始化界面数据
        :return:
        """

        # 从本地文件加载已上传视频数据
        if not os.path.exists(settings.UPLOADED_VIDEO_JSON):
            # 不存在创建文件
            uploaded_json = open(settings.UPLOADED_VIDEO_JSON, mode='w', encoding='utf-8')
            uploaded_json.close()

        with open(settings.UPLOADED_VIDEO_JSON, mode='r', encoding='utf-8') as f:
            uploaded_video_json = f.read()

        if uploaded_video_json:
            self.uploaded_video_list = json.loads(uploaded_video_json)

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
        category_win = VideoCategoryWin(title=settings.CATEGORY_WIN_TITLE)
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
             sg.Text('文件', auto_size_text=True)
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
                    enable_events=True, readonly=True
                ),
                sg.Text(' ' * 6),
                sg.Text('视频子类'),
                sg.Combo(
                    self.sub_categorys, size=(12, 0),
                    key='video_subcategory',
                    auto_size_text=False, readonly=True
                )
            ],
            [sg.Cancel('重 置', key='reset'), sg.T(' ' * 20), sg.Submit('上 传', key='upload')],
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

    def percentage(self, consumed_bytes, total_bytes):
        """
        上传进度计算
        当无法确定待上传的数据长度时，total_bytes的值为None。
        :param consumed_bytes: 已上传字节大小
        :param total_bytes: 总字节大小
        :return:
        """
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            self.upload_rate = rate
            self.current_progress = consumed_bytes
            self.total_value = total_bytes
            print(f'\r已上传{rate}% ', end='')

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

        # if not isinstance(video_subcategory, VideoSubCategory) or \
        #         str(video_subcategory) == '暂无该子分类':
        #     print('暂无该子分类')
        #     return

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
        self.upload_status = UploadStatus.UPLOADING
        self.window.disable()

        # 开线程上传视频
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

        upload_status = self.upload_status

        # 把视频存储到阿里OSS中
        video_item_id = str(int(time.time())) + str(random.randint(100, 999))  # 生成视频唯一id
        video_item_id = int(video_item_id)

        logger.debug(f'视频唯一id -> {video_item_id}, len -> {len(str(video_item_id))}')

        video_save_name = f'{video_item_id}.mp4'
        srt_save_name = f'{video_item_id}.srt'
        oss_save_dir = OSSConfigManage().oss_save_dir

        video_save_path = oss_save_dir + '/' + video_save_name
        srt_save_path = oss_save_dir + '/' + srt_save_name

        try:
            video_url = utils.oss_server.put_obj_from_file(video_save_path, video_path,
                                                           progress_callback=self.percentage)
            srt_url = utils.oss_server.put_obj_from_file(srt_save_path, srt_path, progress_callback=self.percentage)
        except Exception as e:
            # 标记上传失败
            upload_status = UploadStatus.UPLOAD_FAILED
            self.upload_status = upload_status
            self.upload_error = e
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
                create_time = int(time.time())
                hot_feeds = HotFeeds(
                    item_id=video_item_id,
                    create_time=create_time,
                    item_type=video_big_category.category_id,
                    sub_category=video_subcategory.subcategory_id,
                    video_url=video_url,
                    sub_url=srt_url
                )
                session.add(hot_feeds)

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
                # 标记保存视频信息上传到OSS成功, 保存到数据库失败
                upload_status = UploadStatus.UPLOAD_OK_SAVE_FAILED
                self.upload_status = upload_status
                self.upload_error = e

                session.rollback()  # 数据回滚
                logger.error(e)
            else:
                # 标记上传OSS成功并成功保存到数据库
                upload_status = UploadStatus.UPLOAD_OK_SAVE_SUCCESS
                self.upload_status = upload_status
                session.commit()

        if upload_status == UploadStatus.UPLOAD_OK_SAVE_SUCCESS:
            msg = f'上传视频成功, ' \
                  f'所属大类 -> {video_big_category}' \
                  f'所属子类 -> {video_subcategory}'
            logger.info(msg)
            self.reset_info()

        # 记录每个人上传视频的信息到本地文件
        feeds_dict = hot_feeds.as_dict()
        feeds_dict['upload_status'] = upload_status  # 添加一个上传状态信息

        logger.info(feeds_dict)

        self.uploaded_video_list.append(feeds_dict)
        with open(settings.UPLOADED_VIDEO_JSON, mode='w', encoding='utf-8') as f:
            json.dump(self.uploaded_video_list, f, ensure_ascii=False, indent=2)

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
            # if len(self.sub_categorys) == 0:
            #     self.sub_categorys = ['暂无分类']
            #     # self.window['video_subcategory'].update(disabled=True)
            # else:
            #     # self.window['video_subcategory'].update(disabled=False)
            #     pass
            self.window['video_subcategory'].update(values=self.sub_categorys)

    def _check_upload_status(self):
        """
        检测上传视频状态
        :return:
        """

        # 用于开启主窗口可用状态(window.enable)
        status_list = [
            UploadStatus.UPLOAD_FAILED,
            UploadStatus.UPLOAD_OK_SAVE_FAILED,
            UploadStatus.UPLOAD_OK_SAVE_SUCCESS
        ]

        if self.upload_status in status_list:
            sg.OneLineProgressMeterCancel(key='upload_rate')
            # sg.popup_animated(image_source=None)  # 关闭等待动画
            self.window.enable()

        # logger.debug(f'upload_status: {self.upload_status}')

        if self.upload_status == UploadStatus.UPLOADING and self.upload_rate != 101:

            # 正在上传视频
            # sg.popup_animated(image_source=sg.DEFAULT_BASE64_LOADING_GIF, message=f'已上传 {self.upload_rate}%')
            sg.OneLineProgressMeter(
                '上传进度',
                self.current_progress,
                self.total_value,
                'upload_rate',
                '阿里OSS上传进度'
            )
            if self.upload_rate == 100:
                self.upload_rate += 1

        elif self.upload_status == UploadStatus.UPLOAD_FAILED:
            # 上传失败
            self.upload_status = UploadStatus.DEFAULT
            msg = f'上传视频、字幕srt文件到阿里OSS失败\n\n {self.upload_error}'
            sg.popup_error(msg, title='上传失败', text_color=settings.POPUP_ERROR_COLOR, font=settings.POPUP_FONT)

        elif self.upload_status == UploadStatus.UPLOAD_OK_SAVE_FAILED:
            # 上传视频到OSS成功, 但保存数据库失败
            self.upload_status = UploadStatus.DEFAULT
            msg = f'上传视频成功, 但保存视频信息到数据库失败！！！\n\n {self.upload_error}'
            sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)

        elif self.upload_status == UploadStatus.UPLOAD_OK_SAVE_SUCCESS:
            # 成功上传视频到OSS并成功保存到数据库中
            self.upload_status = UploadStatus.DEFAULT
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

            # 视频窗口跳转
            elif 'add_video_category' in event:
                self.add_video_category()
                break
            elif 'del_video_category' in event:
                self.del_video_category()
                break
            elif 'show_uploaded_video' in event or 'show_save_failed_video' in event:
                self.quit()
                UploadedWin(title=settings.UPLOADED_WIN_TITLE).run()
                break
            elif 'db_account_manage' in event or 'oss_account_manage' in event:
                self.quit()
                AccountWin(title=settings.ACCOUNT_WIN_TITLE).run()
                break
            elif 'about_author' in event:
                msg = f'作者：{settings.AUTHOR}\n\n\n' \
                      f'版本：{settings.VERSION}\n\n\n' \
                      f'邮箱：{settings.EMAIL}\n\n\n' \
                      f'简介：{settings.DESC}\n\n\n' \
                      f'{settings.COPYRIGHT}\n'
                sg.popup(msg, title='项目版本信息', font=settings.POPUP_FONT)


def main():
    MainWin(settings.MAIN_WIN_TITLE).run()


if __name__ == '__main__':
    main()
