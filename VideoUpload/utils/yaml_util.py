#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { yaml工具模块 }
# @Date: 2021/05/29 20:32
import yaml
from collections import OrderedDict


def ordered_yaml_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    """
    顺序加载 yaml文件
    """

    class OrderedLoader(Loader):
        pass

    def _construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_yaml_dump(data, stream=None, Dumper=yaml.SafeDumper, object_pairs_hook=OrderedDict, **kwds):
    """
    顺序写入数据到 yaml文件中
    """
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(object_pairs_hook, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def main():
    pass


if __name__ == '__main__':
    main()
