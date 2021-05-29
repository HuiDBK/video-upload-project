#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 阿里OSS对象存储工具模块 }
# @Date: 2021/05/28 18:28
import oss2


def put_obj_from_file(save_path, local_path):
    """
    上传文件到阿里OSS中
    :param save_path: bucket下的保存路径
    :param local_path: 本地文件路径
    :return:
    """
    from settings import OSSConfigManage

    oss_config = OSSConfigManage()

    auth = oss2.Auth(
        access_key_id=oss_config.access_key_id,
        access_key_secret=oss_config.access_key_secret
    )

    bucket = oss2.Bucket(auth, oss_config.endpoint, oss_config.bucket_name)

    bucket.put_object_from_file(save_path, local_path)
    file_url = 'https://' + oss_config.bucket_name + '.' + oss_config.endpoint + '/' + save_path
    return file_url


def main():
    pass


if __name__ == '__main__':
    main()
