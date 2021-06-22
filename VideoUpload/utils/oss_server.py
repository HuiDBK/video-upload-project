#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 阿里OSS对象存储工具模块 }
# @Date: 2021/05/28 18:28
import sys
import oss2


def percentage(consumed_bytes, total_bytes):
    """
    上传进度计算
    :param consumed_bytes: 已上传字节大小
    :param total_bytes: 总字节大小
    :return:
    """
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print(f'\r{rate}% ', end='')
        sys.stdout.flush()


def get_oss_bucket():
    """
    获取 OSS bucket 实例
    :return:
    """
    from settings import OSSConfigManage

    oss_config = OSSConfigManage()

    auth = oss2.Auth(
        access_key_id=oss_config.access_key_id,
        access_key_secret=oss_config.access_key_secret,
    )

    bucket = oss2.Bucket(auth, oss_config.endpoint, oss_config.bucket_name)
    return bucket, oss_config


def delete_object(key):
    """
    删除指定 key的 oss存储文件
    :param key: 文件完整名称
    :return:
    """
    bucket, oss_config = get_oss_bucket()

    # 判断文件是否存在
    exist = bucket.object_exists(key)
    if exist:
        print('object exist')
        bucket.delete_object(key)
    else:
        print('object not exist')


def put_obj_from_file(save_path, local_path, progress_callback=None):
    """
    上传文件到阿里OSS中
    :param save_path: bucket下的保存路径
    :param local_path: 本地文件路径
    :param progress_callback: 上传进度回调函数，默认为 None
    :return:
    """
    bucket, oss_config = get_oss_bucket()
    bucket.put_object_from_file(save_path, local_path, progress_callback=progress_callback)
    file_url = 'https://' + oss_config.bucket_name + '.' + oss_config.endpoint + '/' + save_path
    return file_url


def main():
    access_key_id = 'LTAI5tMJBxZaMasHqM3PPkDi'
    access_key_secret = 'amRZcd3Y8LVcIC4Bnz3dZ2dkzNiiBX'

    auth = oss2.Auth(
        # access_key_id=oss_config.access_key_id,
        # access_key_secret=oss_config.access_key_secret,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    endpoint = 'oss-cn-hangzhou.aliyuncs.com'
    bucket_name = 'gulimail-wwj'
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    file = 'test/test.txt'

    # bucket.put_object(file, 'hello oss')

    exist = bucket.object_exists(file)
    if exist:
        print('object exist')
        bucket.delete_object(file)
    else:
        print('object not exist')


if __name__ == '__main__':
    # main()

    url = 'https://videoex.oss-cn-hongkong.aliyuncs.com/video/1624280262862.mp4'

    ret = url.split('oss-cn-hongkong.aliyuncs.com/')
    print(ret[-1])
    print(ret)