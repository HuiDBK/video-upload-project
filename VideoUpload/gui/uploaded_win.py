#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 已上传视频窗口模块 }
# @Date: 2021/05/30 23:18
import time
import json
import logging
import requests
import settings
from gui import BaseWin
import PySimpleGUI as sg
from pysubs2 import SSAFile
from models import DBSession
from utils import oss_server
from settings import UploadStatus
from settings import OSSConfigManage
from models import HotFeeds, SubTitle
from datetime import datetime, timedelta
from sqlalchemy.exc import DatabaseError

logger = logging.getLogger('server')


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

        # 上传到 OSS 所有的视频信息
        self.uploaded_video_list = list()

        # 用于获取已上传成功视频信息的数据列表
        self.upload_success_video_info = list()

        # 用于获取成功上传到OSS, 但保存到数据库失败的视频信息的数据列表
        self.save_failed_video_info = list()

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

    def _create_upload_success_frame(self, data):
        """
        创建 视频上传到OSS成功, 保存数据库成功的布局
        :param data: 成功视频数据
        :return: upload_success_frame
        """
        upload_success_frame = [
            [
                sg.Table(
                    values=data,
                    headings=self.hot_feeds_cols,
                    header_background_color=settings.TAB_HEADER_BG_COLOR,
                    header_text_color=settings.TAB_HEADER_TEXT_COLOR,
                    enable_events=True,
                    auto_size_columns=False,
                    def_col_width=settings.TAB_DEF_WIDTH,
                    font=settings.TAB_HEADER_FONT,
                    row_height=settings.TAB_ROW_HEIGHT,
                    justification=settings.TAB_ALIGN,
                    key='upload_success_table'
                )
            ]
        ]

        return upload_success_frame

    def _create_save_failed_frame(self, data):
        """
        创建 视频上传到OSS成功, 保存数据库失败的布局
        :param data: 上传到OSS成功, 数据库保存失败的视频数据
        :return: save_failed_frame
        """

        # 上传失败的视频信息, id为None故去除
        data = [items[1:] for items in data]
        save_failed_frame = [
            [
                sg.Table(
                    values=data,
                    headings=self.hot_feeds_cols[1:],
                    header_background_color=settings.TAB_HEADER_BG_COLOR,
                    header_text_color=settings.TAB_HEADER_TEXT_COLOR,
                    enable_events=True,
                    auto_size_columns=False,
                    def_col_width=settings.TAB_DEF_WIDTH,
                    font=settings.TAB_HEADER_FONT,
                    row_height=settings.TAB_ROW_HEIGHT,
                    justification=settings.TAB_ALIGN,
                    key='save_failed_table'
                )
            ]
        ]

        return save_failed_frame

    def init_layout(self):
        """
        初始化已上传视频窗口布局
        :return:
        """

        # 用于获取已上传成功视频信息的表格格式数据列表
        upload_success_video_info = list()

        # 用于获取成功上传到OSS, 但保存到数据库失败的视频信息的表格格式数据列表
        save_failed_video_info = list()

        for uploaded_video_dict in self.uploaded_video_list:
            video_items = list()
            for key, value in uploaded_video_dict.items():
                if key == 'create_time':
                    # 把视频创建时间戳转成具体日期
                    time_local = time.localtime(int(value))
                    value = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
                video_items.append(value)

            upload_status = uploaded_video_dict.get('upload_status')

            if upload_status == UploadStatus.UPLOAD_OK_SAVE_SUCCESS:
                self.upload_success_video_info.append(uploaded_video_dict)
                upload_success_video_info.append(video_items)
            elif upload_status == UploadStatus.UPLOAD_OK_SAVE_FAILED:
                self.save_failed_video_info.append(uploaded_video_dict)
                save_failed_video_info.append(video_items)

        upload_success_frame = self._create_upload_success_frame(data=upload_success_video_info)
        save_failed_frame = self._create_save_failed_frame(data=save_failed_video_info)

        upload_success_info_tab = sg.Tab(
            title='上传成功视频数据',
            key='upload_success_tab',
            layout=[
                [sg.Column(upload_success_frame)]
            ],
            element_justification='center'
        )

        save_failed_info_tab = sg.Tab(
            title='数据库保存失败视频数据',
            key='save_failed_tab',
            layout=[
                [sg.Column(save_failed_frame)],
                [sg.Button('删除视频和字幕文件', key='delete_oss_info'),
                 sg.T(),
                 sg.Button('重新保存到数据库', key='restock2db')]
            ],
            element_justification='center'
        )

        uploaded_info_tab_group = sg.TabGroup(
            [[upload_success_info_tab, save_failed_info_tab]],
            key='uploaded_tab_group',
            enable_events=True,
            selected_background_color=settings.TAB_SELECTED_COLOR
        )

        layout = [
            [sg.Menu(self.menus, font=settings.MENU_FONT)],
            [sg.Button(settings.MAIN_WIN_TITLE, key='main_win_btn'),
             sg.Button(settings.CATEGORY_WIN_TITLE, key='category_win_btn'),
             sg.Button(settings.ACCOUNT_WIN_TITLE, key='account_win_btn')
             ],
            [sg.pin(uploaded_info_tab_group)]
        ]
        return layout

    def update_save_failed_info(self):
        """
        更新保存失败的表格视频信息
        :return:
        """
        save_failed_video_info = list()

        for uploaded_video_dict in self.save_failed_video_info:
            video_items = list()
            for key, value in uploaded_video_dict.items():
                video_items.append(value)
            save_failed_video_info.append(video_items)

        save_failed_video_info = [items[1:] for items in save_failed_video_info]
        self.window['save_failed_table'].update(values=save_failed_video_info)

    def update_success_video_info(self):
        """
        更新上传成功表格数据界面
        :return:
        """
        upload_success_video_info = list()

        for video_dict in self.upload_success_video_info:
            video_items = list()
            for key, value in video_dict.items():
                if key == 'create_time':
                    # 把视频创建时间戳转成具体日期
                    time_local = time.localtime(int(value))
                    value = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
                video_items.append(value)
            upload_success_video_info.append(video_items)

        self.window['upload_success_table'].update(values=upload_success_video_info)

    @staticmethod
    def delete_local_uploaded_info(item_id):
        """
        根据 item_id 删除本地对应的上传视频信息
        :param item_id: 视频上传信息唯一id
        :return:
        """

        print(item_id)
        with open(settings.UPLOADED_VIDEO_JSON, mode='r', encoding='utf-8') as f:
            uploaded_video_json_str = f.read()

        if uploaded_video_json_str:
            uploaded_video_list = json.loads(uploaded_video_json_str)

            # 过滤删除了OSS文件的本地信息
            uploaded_video_list = [video_items for video_items in uploaded_video_list
                                   if video_items['item_id'] != item_id]

            # 过滤后重新写入本地文件
            with open(settings.UPLOADED_VIDEO_JSON, mode='w', encoding='utf-8') as f:
                json.dump(uploaded_video_list, f, ensure_ascii=False, indent=2)

    def _delete_oss_info(self, value_dict: dict):
        """
        删除指定的 OSS上的视频信息
        :param value_dict:
        :return:
        """
        select_ret = value_dict.get('save_failed_table')

        if not select_ret:
            msg = '请选择要删除的视频信息条目\n'
            sg.popup(msg, title='没有选择视频信息', font=settings.POPUP_FONT)
            return

        # 获取选择索引
        index = select_ret[0]

        # 根据索引获取保存失败的视频信息
        failed_video_infos = self.save_failed_video_info[index]

        print(index)
        print(failed_video_infos)

        # 删除 OSS 上的对应的视频信息
        video_url = failed_video_infos.get('video_url')
        sub_url = failed_video_infos.get('sub_url')

        print(video_url)
        print(sub_url)

        oss_config = OSSConfigManage()
        video_key = str(video_url).split(oss_config.endpoint + '/')[-1]
        sub_key = str(sub_url).split(oss_config.endpoint + '/')[-1]

        print(video_key)
        print(sub_key)

        msg = f'确认删除如下视频信息\n\n' \
              f'视频: {video_key} \n\n' \
              f'字幕: {sub_key} \n\n'

        ret = sg.popup_yes_no(
            msg,
            title='确认删除',
            font=settings.POPUP_FONT,
            text_color=settings.POPUP_ERROR_COLOR
        )

        print(ret)

        if str(ret).lower() == 'yes':
            try:
                oss_server.delete_object(video_key)
                oss_server.delete_object(sub_key)
            except Exception as e:
                logger.error(e)
                msg = '删除 OSS 视频信息失败\n\n' + str(e)
                sg.popup_error(msg, title='删除失败', font=settings.POPUP_FONT)
                return
            else:

                # 删除成功, 更新本地文件, 及当前显示的界面
                del self.save_failed_video_info[index]
                self.update_save_failed_info()

                item_id = failed_video_infos.get('item_id')
                self.delete_local_uploaded_info(item_id)

                msg = f'视频: {video_key} \n\n' \
                      f'字幕: {sub_key} \n\n' \
                      f'删除成功 \n'
                sg.popup(msg, title='删除成功', font=settings.POPUP_FONT, text_color=settings.POPUP_SUCCESS_COLOR)
        else:
            print('取消删除')

    def _restock2db(self, value_dict):
        """
        重新保存到数据库
        :param value_dict:
        :return:
        """
        select_ret = value_dict.get('save_failed_table')

        if not select_ret:
            msg = '请选择要重新保存的视频信息条目\n'
            sg.popup(msg, title='没有选择视频信息', font=settings.POPUP_FONT)
            return

        # 获取选择索引
        index = select_ret[0]

        # 根据索引获取保存失败的视频信息
        failed_video_infos = self.save_failed_video_info[index]
        print(index)
        print(failed_video_infos)

        video_url = failed_video_infos.get('video_url')
        sub_url = failed_video_infos.get('sub_url')

        # 提取OSS中srt字幕相关数据
        srt_str = requests.get(sub_url).text
        subs = SSAFile.from_string(srt_str, encoding='utf-8')

        # 保存到数据库中
        with DBSession() as session:
            try:
                # 保存视频信息到数据库
                create_time = int(time.time())
                hot_feeds = HotFeeds(
                    item_id=failed_video_infos.get('item_id'),
                    create_time=create_time,
                    item_type=failed_video_infos.get('item_type'),
                    sub_category=failed_video_infos.get('sub_category'),
                    video_url=video_url,
                    sub_url=sub_url
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
                        item_id=failed_video_infos.get('item_id')
                    )
                    session.add(sub_title)
            except (Exception, DatabaseError) as e:
                # 保存到数据库失败
                # upload_status = UploadStatus.UPLOAD_OK_SAVE_FAILED
                # self.upload_status = upload_status
                # self.upload_error = e

                session.rollback()  # 数据回滚
                logger.error(e)
                msg = '视频信息重新保存到数据库失败\n\n' + str(e)
                sg.popup(msg, title='重新保存失败', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)
            else:
                # 标记上传OSS成功并成功保存到数据库
                # upload_status = UploadStatus.UPLOAD_OK_SAVE_SUCCESS
                # self.upload_status = upload_status
                session.commit()

                # 重新保存成功更新页面表格数据, 并更新本地json文件
                del self.save_failed_video_info[index]
                self.update_save_failed_info()

                # 先删除本地重新保存成功的视频信息
                self.delete_local_uploaded_info(failed_video_infos['item_id'])

                # 把保存到数据库中的数据重新写入到本地json文件
                feeds_dict = hot_feeds.as_dict()

                # 更新上传成功视频信息的表格页面数据
                self.upload_success_video_info.append(feeds_dict)
                self.update_success_video_info()
                feeds_dict['upload_status'] = UploadStatus.UPLOAD_OK_SAVE_SUCCESS

                logger.info(feeds_dict)

                with open(settings.UPLOADED_VIDEO_JSON, mode='w', encoding='utf-8') as f:
                    json.dump(self.upload_success_video_info, f, ensure_ascii=False, indent=2)

                msg = '视频信息重新保存到数据库成功\n'
                sg.popup(msg, title='重新保存成功', font=settings.POPUP_FONT, text_color=settings.POPUP_SUCCESS_COLOR)

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
            elif event == 'delete_oss_info':
                self._delete_oss_info(value_dict)
            elif event == 'restock2db':
                self._restock2db(value_dict)

    def run(self):
        self._event_handler()


def main():
    UploadedWin(settings.UPLOADED_WIN_TITLE).run()


if __name__ == '__main__':
    main()
