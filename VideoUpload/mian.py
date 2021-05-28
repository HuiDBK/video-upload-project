#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目主入口模块 }
# @Date: 2021/05/21 13:04
import logging
import settings


def main():
    settings.setup_logging()
    logger = logging.getLogger('server')

    logger.debug('debug log test')
    logger.info('info log test')
    logger.warning('warning log test')
    logger.error('error log test')


if __name__ == '__main__':
    main()
