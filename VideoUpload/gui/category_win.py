#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 视频分类管理模块 }
# @Date: 2021/05/29 12:54
import logging
import settings
import threading
from gui import BaseWin
import PySimpleGUI as sg
from sqlalchemy import or_
from sqlalchemy.exc import DatabaseError
from models import DBSession, VideoCategory, VideoSubCategory

logger = logging.getLogger('server')


class VideoCategoryWin(BaseWin):
    """视频分类管理窗口"""

    menus = [
        ['窗口跳转', [
            '上传视频窗口::back_main_win']],
        ['数据同步刷新', [
            '视频分类数据同步::video_category_synchronize']]
    ]

    def __init__(self, title):
        # 标记数据库是否异常
        self.db_error_flag = None

        self.all_video_category = list()
        self.all_video_subcategory = list()

        # 视频分类表字段名称
        self.video_category_cols = [col.comment for col in VideoCategory.__table__.columns]
        self.video_subcategory_cols = [col.comment for col in VideoSubCategory.__table__.columns]

        self.init_video_data()
        super().__init__(title)

    def init_video_data(self):
        """
        初识化视频数据
        :return:
        """
        init_data_th = threading.Thread(target=self._init_video_data)
        init_data_th.start()

    def _init_video_data(self):
        """初始化视频分类数据"""
        self.db_error_flag = None

        with DBSession() as session:
            # 获取视频分类数据
            try:
                self.all_video_category = session.query(VideoCategory).all()
                self.all_video_subcategory = session.query(VideoSubCategory).all()
            except DatabaseError as e:
                logger.error(e)
                self.db_error_flag = True  # 标记数据库异常
            else:
                self.db_error_flag = False  # 查询数据库成功

    def _create_video_category_frame(self):
        """
        创建视频大分类表格布局
        :return:
        """
        # 视频大分类数据
        video_category_data = self.get_video_category_data()

        # 视频大分类表格布局
        video_category_frame = [
            [sg.Table(
                headings=self.video_category_cols,
                values=video_category_data,
                header_background_color=settings.TAB_HEADER_BG_COLOR,
                header_text_color=settings.TAB_HEADER_TEXT_COLOR,
                enable_events=True,
                auto_size_columns=False,
                def_col_width=settings.TAB_DEF_WIDTH,
                font=settings.TAB_HEADER_FONT,
                row_height=settings.TAB_ROW_HEIGHT,
                justification=settings.TAB_ALIGN,
                key='video_category_table',
                pad=(60, settings.ELEMENT_PAD[1]),
            )]
        ]
        return video_category_frame

    def _create_subcategory_frame(self):
        """
        创建视频子分类表格布局
        :return:
        """
        # 视频子分类数据
        video_subcategory_data = self.get_video_subcategory_data()

        # 视频子分类表格布局
        video_subcategory_frame = [
            [sg.Table(
                headings=self.video_subcategory_cols,
                values=video_subcategory_data,
                header_background_color=settings.TAB_HEADER_BG_COLOR,
                header_text_color=settings.TAB_HEADER_TEXT_COLOR,
                enable_events=True,
                auto_size_columns=False,
                def_col_width=settings.TAB_DEF_WIDTH,
                row_height=settings.TAB_ROW_HEIGHT,
                font=settings.TAB_HEADER_FONT,
                justification=settings.TAB_ALIGN,
                key='video_subcategory_table')],
        ]
        return video_subcategory_frame

    def get_video_category_data(self):
        """
        获取视频大分类数据，用于表格的显示
        :return:
        """
        video_category_data = list()
        for video_category in self.all_video_category:
            rows = [video_category.id, video_category.category_id, video_category.category_name]
            video_category_data.append(rows)
        return video_category_data

    def get_video_subcategory_data(self):
        """
        获取视频子分类数据，用于表格的显示
        :return:
        """
        video_subcategory_data = list()
        for subcategory in self.all_video_subcategory:
            rows = [subcategory.id, subcategory.subcategory_id, subcategory.subcategory_name, subcategory.parent_id]
            video_subcategory_data.append(rows)
        return video_subcategory_data

    def _update_video_category(self):
        """
        更新视频大分类数据
        :return:
        """
        video_category_data = self.get_video_category_data()
        self.window['video_category_table'].update(values=video_category_data)

    def _update_video_subcategory(self):
        """
        更新视频子分类数据
        :return:
        """
        video_sub_category_data = self.get_video_subcategory_data()

        self.window['video_subcategory_table'].update(values=video_sub_category_data)
        self.window['video_category_combo'].update(values=self.all_video_category)

    def init_layout(self):
        """初始化视频分类窗口布局"""

        video_category_frame = self._create_video_category_frame()
        video_subcategory_frame = self._create_subcategory_frame()

        add_big_category_layout = [
            [sg.Text('大分类id  '), sg.Input(size=(20, 15), key='input_big_category_id')],
            [sg.Text('大分类名称'), sg.Input(size=(20, 15), key='input_big_category_name')],
            [sg.Button('新增视频大分类', key='add_big_category'),
             sg.Button('删除视频大分类', key='del_big_category')]
        ]

        video_category_tab = sg.Tab(
            title='视频大分类',
            key='big_category_tab',
            layout=[
                [sg.Column(video_category_frame), sg.Column(add_big_category_layout)],
            ]
        )

        add_subcategory_layout = [
            [sg.Text('子分类id  '), sg.Input(size=(15, 15), key='input_subcategory_id')],
            [sg.Text('子分类名称'), sg.Input(size=(15, 15), key='input_subcategory_name')],
            [sg.Text('所属父分类'), sg.Combo(self.all_video_category, key='video_category_combo', readonly=True)],
            [sg.Button('新增视频子分类', key='add_subcategory'), sg.Button('删除视频子分类', key='del_subcategory')]
        ]

        video_subcategory_tab = sg.Tab(
            title='视频子分类',
            key='subcategory_tab',
            layout=[
                [sg.Column(video_subcategory_frame), sg.Column(add_subcategory_layout)]
            ]
        )

        # 视频分类tab_group
        category_tab_group = sg.TabGroup(
            [[video_category_tab, video_subcategory_tab]],
            key='category_tab_group',
            enable_events=True,
            selected_background_color=settings.TAB_SELECTED_COLOR)

        layout = [
            [sg.Menu(self.menus, font=settings.MENU_FONT)],
            [sg.pin(category_tab_group)]
        ]
        return layout

    def run(self):
        self._event_handler()

    def _del_video_subcategory(self, value_dict):
        """
        删除视频子分类
        :param value_dict:事件响应信息字典
        :return:
        """
        video_subcategory = value_dict.get('video_subcategory_table')

        if len(video_subcategory) == 0 or video_subcategory is None:
            sg.Popup('请选择表格中你要删除的子分类数据\n', title='请选择', font=settings.POPUP_FONT)
            return

        # 获取所选表格的下标
        index = video_subcategory[0]
        logger.debug(f'所选视频子分类表格行 -> {index}')
        video_subcategory_obj = self.all_video_subcategory[index]

        msg = f'确认删除视频子分类【 {video_subcategory_obj} 】\n\n' \
              f'子分类id  ->  {video_subcategory_obj.subcategory_id}\n\n' \
              f'子分类名  ->  {video_subcategory_obj.subcategory_name}\n'
        ret = sg.popup_yes_no(msg, title='确认删除子分类', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)

        if ret is not None and ret.lower() == 'yes':
            # 数据库删除子分类数据
            with DBSession() as session:
                try:
                    session.delete(video_subcategory_obj)
                    session.commit()
                except DatabaseError as e:
                    logger.error(e)
                    content = f'分类【 {video_subcategory_obj.subcategory_name} 】删除失败，数据库异常！！！\n'
                    sg.popup_error(content, title='数据库异常', text_color=settings.POPUP_ERROR_COLOR,
                                   font=settings.POPUP_FONT)
                    return

            # 更新子分类表格数据
            del self.all_video_subcategory[index]
            self._update_video_subcategory()

            msg = f'子分类【 {video_subcategory_obj.subcategory_name} 】删除成功\n\n' \
                  f'子分类id  ->  {video_subcategory_obj.subcategory_id}\n\n' \
                  f'子分类名  ->  {video_subcategory_obj.subcategory_name}\n'
            logger.info(msg)
            sg.Popup(msg, title='删除成功', text_color=settings.POPUP_SUCCESS_COLOR, font=settings.POPUP_FONT)

    def _del_video_big_category(self, value_dict):
        """
        删除视频大分类
        :param value_dict: 事件响应信息字典
        :return:
        """
        video_category = value_dict.get('video_category_table')

        if len(video_category) == 0 or video_category is None:
            sg.Popup('请选择你要删除的分类数据\n', title='请选择', font=settings.POPUP_FONT)
            return

        # 获取视频大分类所选表格行即下标
        index = video_category[0]
        logger.debug(f'所选视频大分类表格行 -> {index}')
        video_category_obj = self.all_video_category[index]

        msg = f'确认删除大分类【{video_category_obj}】\n\n' \
              f'大分类id  ->  {video_category_obj.category_id}\n\n' \
              f'大分类名  ->  {video_category_obj.category_name}\n'
        ret = sg.popup_yes_no(msg, title='确认删除大分类', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)

        if ret is not None and ret.lower() == 'yes':
            # 数据库删除视频大分类数据
            with DBSession() as session:
                try:
                    session.delete(video_category_obj)  # 删除视频大分类, 级联删除相关联的子分类
                except DatabaseError as e:
                    session.rollback()  # 发送错误，回滚数据
                    logger.error(e)
                    msg = f'分类【 {video_category_obj.category_name} 】删除失败，数据库异常！！！\n'
                    sg.popup_error(msg, title='数据库异常', text_color=settings.POPUP_ERROR_COLOR, font=settings.POPUP_FONT)
                    return
                else:
                    session.commit()

            # 更新大分类数据
            del self.all_video_category[index]
            self._update_video_category()

            # 更新子分类数据
            self.all_video_subcategory = [video_subcategory for video_subcategory in self.all_video_subcategory
                                          if video_subcategory.parent_id != video_category_obj.id]

            self._update_video_subcategory()

            msg = f'分类【 {video_category_obj.category_name} 】删除成功\n\n' \
                  f'分类id  ->  {video_category_obj.category_id}\n\n' \
                  f'分类名  ->  {video_category_obj.category_name}\n'
            logger.info(msg)
            sg.Popup(msg, title='删除成功', text_color=settings.POPUP_SUCCESS_COLOR, font=settings.POPUP_FONT)

    def add_video_big_category(self, value_dict: dict):
        """
        新增视频大分类
        :param value_dict: 事件响应信息字典
        :return:
        """
        big_category_id = value_dict.get('input_big_category_id')
        big_category_name = value_dict.get('input_big_category_name')

        # 校验参数
        if not all([big_category_id, big_category_name]):
            sg.popup('新增视频大分类参数不完整!!!\n', title='新增视频大分类', font=settings.POPUP_FONT)
            return

        # 判断分类id是否是数字
        if str(big_category_id).isnumeric():
            big_category_id = int(big_category_id)
        else:
            sg.popup('分类id需为整型，参数类型错误!!!\n', title='新增视频大分类', font=settings.POPUP_FONT)
            return

        # 判断是否存在相同的分类
        with DBSession() as session:
            try:
                query_ret = session.query(VideoCategory.id) \
                    .filter(or_(VideoCategory.category_id == big_category_id,
                                VideoCategory.category_name == big_category_name)) \
                    .count()
            except DatabaseError as e:
                logger.error(e)
                msg = f'数据库异常, 添加视频【 {big_category_name} 】分类失败\n\n' \
                      f'分类id  ->  {big_category_id}\n\n' \
                      f'分类名  ->  {big_category_name}\n'
                sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)
                return

        if query_ret != 0:
            msg = f'视频分类重复, 请重新修改\n\n' \
                  f'分类id  ->  {big_category_id}\n\n' \
                  f'分类名  ->  {big_category_name}\n'
            sg.Popup(msg, title='分类重复', font=settings.POPUP_FONT)
            return

        # 保存新增的分类到数据库
        with DBSession() as session:
            try:
                new_video_category = VideoCategory(category_id=big_category_id, category_name=big_category_name)
                session.add(new_video_category)
                session.commit()
            except DatabaseError as e:
                logger.error(e)
                msg = f'数据库异常, 添加视频【 {big_category_name} 】分类失败\n\n' \
                      f'分类id  ->  {big_category_id}\n\n' \
                      f'分类名  ->  {big_category_name}\n'
                sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)
                return

        # 添加成功清除输入的分类信息
        self.window['input_big_category_id'].update('')
        self.window['input_big_category_name'].update('')

        # 更新窗口数据
        self.all_video_category.append(new_video_category)
        self._update_video_category()
        self._update_video_subcategory()
        msg = f'添加视频分类【 {big_category_name} 】成功\n\n' \
              f'分类id  ->  {big_category_id}\n\n' \
              f'分类名  ->  {big_category_name}\n'
        logger.info(msg)
        sg.Popup(msg, title='添加分类成功', font=settings.POPUP_FONT, text_color=settings.POPUP_SUCCESS_COLOR)

    def add_video_subcategory(self, value_dict: dict):
        """
        新增视频子分类
        :param value_dict: 事件响应信息字典
        :return:
        """
        subcategory_id = value_dict.get('input_subcategory_id')
        subcategory_name = value_dict.get('input_subcategory_name')
        parent_category = value_dict.get('video_category_combo')

        logger.debug(f'subcategory_id -> {subcategory_id}')
        logger.debug(f'subcategory_name -> {subcategory_name}')
        logger.debug(f'parent_category -> {parent_category}')

        # 校验参数
        params = [subcategory_id, subcategory_name, parent_category]
        if not all(params):
            sg.popup('新增视频子分类参数不完整!!!\n', title='新增视频子分类', font=settings.POPUP_FONT)
            return

        # 判断分类id是否是数字
        if str(subcategory_id).isnumeric():
            subcategory_id = int(subcategory_id)
        else:
            sg.popup('分类id需为整型，参数类型错误!!!\n', title='新增视频子分类', font=settings.POPUP_FONT)
            return

        # 判断是否存在相同的分类
        with DBSession() as session:
            try:
                query_ret = session.query(VideoSubCategory.id) \
                    .filter(or_(VideoSubCategory.subcategory_id == subcategory_id,
                                VideoSubCategory.subcategory_name == subcategory_name)) \
                    .count()
            except DatabaseError as e:
                logger.error(e)
                msg = f'数据库异常, 添加视频【 {subcategory_name} 】子分类失败\n\n' \
                      f'子分类id  ->  {subcategory_id}\n\n' \
                      f'子分类名  ->  {subcategory_name}\n'
                sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)
                return

        if query_ret != 0:
            msg = f'视频子分类重复, 请重新修改\n\n' \
                  f'子分类id  ->  {subcategory_id}\n\n' \
                  f'子分类名  ->  {subcategory_name}\n'
            sg.Popup(msg, title='子分类重复', font=settings.POPUP_FONT)
            return

        # 保存新增的子分类到数据库
        with DBSession() as session:
            try:
                new_video_subcategory = VideoSubCategory(
                    subcategory_id=subcategory_id,
                    subcategory_name=subcategory_name,
                    parent_id=parent_category.category_id
                )
                session.add(new_video_subcategory)
                session.commit()
            except DatabaseError as e:
                logger.error(e)
                msg = f'数据库异常, 添加视频【 {subcategory_name} 】子分类失败\n\n' \
                      f'子分类id  ->  {subcategory_id}\n\n' \
                      f'子分类名  ->  {subcategory_name}\n'
                sg.popup_error(msg, title='数据库异常', font=settings.POPUP_FONT, text_color=settings.POPUP_ERROR_COLOR)
                return

        # 添加成功清除输入的分类信息
        self.window['input_subcategory_id'].update('')
        self.window['input_subcategory_name'].update('')
        self.window['video_category_combo'].update('')

        # 更新窗口数据
        self.all_video_subcategory.append(new_video_subcategory)
        self._update_video_subcategory()
        msg = f'添加视频子分类【 {subcategory_name} 】成功\n\n' \
              f'子分类id  ->  {subcategory_id}\n\n' \
              f'子分类名  ->  {subcategory_name}\n\n' \
              f'父分类名  ->  {parent_category.category_name}\n'
        logger.info(msg)
        sg.popup(msg, title='添加子分类成功', font=settings.POPUP_FONT, text_color=settings.POPUP_SUCCESS_COLOR)

    def _event_handler(self):
        """
        窗口事件监听
        :return:
        """
        self.window.disable()  # 数据未获取让窗口不可用
        while True:
            event, value_dict = self.window.read(timeout=10)
            # logger.debug(f'db_error_flag -> {self.db_error_flag}')

            if self.db_error_flag is None:
                self.window.disable()  # 数据未获取让窗口不可用
                win_gif = settings.WIN_GIF or sg.DEFAULT_BASE64_LOADING_GIF
                sg.popup_animated(image_source=win_gif, message='加载数据中...')
                continue
            elif self.db_error_flag is True:
                # 数据库异常
                self.window.enable()
                sg.popup_animated(image_source=None)  # 关闭加载动画
                sg.popup_error('无法获取视频分类数据，数据库异常！！！', title='数据库异常', font=settings.POPUP_FONT)
                self.db_error_flag = -1  # 提示信息只显示一次
            elif self.db_error_flag is False:
                # 获取数据库数据成功
                logger.debug('query db data success')
                self.window.enable()
                sg.popup_animated(image_source=None)
                self._update_video_category()
                self._update_video_subcategory()
                self.db_error_flag = 0

            if event in (sg.WIN_CLOSED, 'Quit') or 'back_main_win' in event:
                self.quit()
                from gui.main_win import MainWin
                main_win = MainWin('main')
                main_win.run()
                break

            elif 'video_category_synchronize' in event:
                # 视频分类数据同步刷新
                self.init_video_data()
                self._update_video_category()
                self._update_video_subcategory()
            elif event == 'del_big_category':
                self._del_video_big_category(value_dict)
            elif event == 'del_subcategory':
                self._del_video_subcategory(value_dict)
            elif event == 'add_big_category':
                self.add_video_big_category(value_dict)
            elif event == 'add_subcategory':
                self.add_video_subcategory(value_dict)


def main():
    VideoCategoryWin('category').run()


if __name__ == '__main__':
    main()
