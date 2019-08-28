#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, Vinman, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.cub@gmail.com>

import os
import sys
import logging


class Rule(object):
    def __init__(self, root, **kwargs):
        logger = kwargs.pop('logger', None)
        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            if not self.logger.handlers:
                stream_hander = logging.StreamHandler(sys.stdout)
                stream_hander.setLevel(logging.DEBUG)
                self.logger.addHandler(stream_hander)
            self.logger.setLevel(logging.DEBUG)

        self.root = root
        self.ignore_equals = set()  # 等于xxx的忽略规则
        self.ignore_startswith = set()  # 以xxx开头的忽略规则
        self.ignore_endswith = set()  # 以xxx结尾的忽略规则
        self.ignore_contains = set()  # 以包含xxx的忽略规则
        self.ignore_abs_startswith = set()  # 绝对路径以xxx开头的忽略规则
        self.ignore_abs_equals = set()  # 绝对路径等于xxx的忽略规则

        self.include_abs_startswith = set()  # 包含以xxx开头的
        self.include_abs_equals = set()  # 包含绝对路径等于xxx的
        try:
            if self.root and os.path.exists(self.root):
                self.read_ignore_config()
        except Exception as e:
            logger.error(e)

    def read_ignore_config(self):
        path = os.path.join(os.getcwd(), '.syncignore') if hasattr(sys, 'frozen') \
            else os.path.join(os.getcwd(), 'spec', 'dist', '.syncignore')
        if not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('!'):
                # 强制不被忽略的规则
                line = line[1:]
                if not line:
                    continue
                if line.endswith('*'):
                    line = line[:-1]
                    if not line:
                        continue
                    if line.startswith('/'):
                        line = line[1:]
                        if not line:
                            continue
                        p = os.path.abspath(os.path.join(self.root, line))
                        if os.path.exists(p):
                            self.include_abs_startswith.add(p)
                    if os.path.exists(line) and os.path.isabs(line):
                        self.include_abs_startswith.add(os.path.abspath(line))
                else:
                    if line.startswith('/'):
                        line = line[1:]
                        if not line:
                            continue
                        p = os.path.abspath(os.path.join(self.root, line))
                        if os.path.exists(p):
                            self.include_abs_equals.add(p)
                    elif os.path.exists(line) and os.path.isabs(line):
                        self.include_abs_equals.add(os.path.abspath(line))
            else:
                # 忽略的规则
                if line.startswith('*'):
                    line = line[1:].strip()
                    if not line:
                        continue
                    if line.endswith('*'):
                        line = line[:-1]
                        if not line:
                            continue
                        self.ignore_contains.add(line)
                    else:
                        self.ignore_endswith.add(line)
                else:
                    if line.endswith('*'):
                        line = line[:-1]
                        if not line:
                            continue
                        if line.startswith('/'):
                            line = line[1:]
                            if not line:
                                continue
                            p = os.path.abspath(os.path.join(self.root, line))
                            if os.path.exists(p):
                                self.ignore_abs_startswith.add(p)
                        elif os.path.exists(line) and os.path.isabs(line):
                            self.ignore_abs_startswith.add(os.path.abspath(line))
                        else:
                            self.ignore_startswith.add(line)
                    elif line.startswith('/'):
                        line = line[1:]
                        if not line:
                            continue
                        p = os.path.abspath(os.path.join(self.root, line))
                        if os.path.exists(p):
                            self.ignore_abs_equals.add(p)
                    elif os.path.exists(line) and os.path.isabs(line):
                        self.ignore_abs_equals.add(os.path.abspath(line))
                    else:
                        self.ignore_equals.add(line.rstrip('/'))

        self.logger.debug('=' * 60)
        self.logger.debug('忽略名字开头: {}'.format(self.ignore_startswith))
        self.logger.debug('忽略名字结尾: {}'.format(self.ignore_endswith))
        self.logger.debug('忽略名字包含: {}'.format(self.ignore_contains))
        self.logger.debug('忽略名字等于: {}'.format(self.ignore_equals))
        self.logger.debug('忽略绝对路径开头: {}'.format(self.ignore_abs_startswith))
        self.logger.debug('忽略绝对路径等于: {}'.format(self.ignore_abs_equals))
        self.logger.debug('包含绝对路径开头: {}'.format(self.include_abs_startswith))
        self.logger.debug('包含绝对路径等于: {}'.format(self.include_abs_equals))

    def check_is_ignore(self, path, name=None):
        if name is None:
            name = os.path.split(path)[1]
        path = os.path.abspath(path)
        if path in self.include_abs_equals:
            return False
        if path.startswith(tuple(self.include_abs_startswith)):
            return False
        if path in self.ignore_abs_equals:
            return True
        if path.startswith(tuple(self.ignore_abs_startswith)):
            return True
        if name in self.ignore_equals:
            return True
        if name.startswith(tuple(self.ignore_startswith)):
            return True
        if name.endswith(tuple(self.ignore_endswith)):
            return True
        for item in self.ignore_contains:
            if item in name:
                return True
        return False

if __name__ == '__main__':
    rule = Rule('E:\\Vinman')

