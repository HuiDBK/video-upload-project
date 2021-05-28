#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 阿里OSS对象存储工具模块 }
# @Date: 2021/05/28 18:28
import oss2
import settings


auth = oss2.Auth(
    access_key_id=settings.ACCESS_KEY_ID,
    access_key_secret=settings.ACCESS_KEY_SECRET
)

bucket = oss2.Bucket(auth, settings.ENDPOINT, settings.BUCKET_NAME)


def put_obj_from_file(save_path, local_path):
    """
    上传文件到阿里OSS中
    :param save_path: bucket下的保存路径
    :param local_path: 本地文件路径
    :return:
    """
    bucket.put_object_from_file(save_path, local_path)
    file_url = 'https://' + settings.BUCKET_NAME + '.' + settings.ENDPOINT + '/' + save_path
    return file_url


def main():
    pass


if __name__ == '__main__':
    main()
