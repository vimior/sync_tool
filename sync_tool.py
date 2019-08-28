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
import time
import stat
import shutil
import hashlib
import threading
import queue
from rule.rule import Rule
from common.log import logger
from common.config import ConfigTemplate, DefaultConfig


class WorkThread(threading.Thread):
    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.pool = pool
        self.finished = True
        self.success_count = 0
        self.failed_count = 0
        self.copy_count = 0
        self.start()

    def run(self):
        while self.pool.alive:
            try:
                if self.pool.que.empty():
                    time.sleep(0.1)
                    continue
                item = self.pool.que.get(timeout=1)
                self.finished = False
                func = item['func']
                self.copy_count += func(*item['args'], **item['kwargs'])
                self.success_count += 1
                self.finished = True
            except Exception as e:
                logger.error('[任务失败] {}'.format(e))
                self.failed_count += 1
                time.sleep(0.1)


class ThreadPool(object):
    def __init__(self, thread_size=10):
        self.que = queue.Queue()
        self.alive = True
        self.task_count = 0
        self.thread_size = thread_size
        self.threads = [WorkThread(self) for _ in range(thread_size)]

    def stop(self):
        self.alive = False

    def add_task(self, task, *args, **kwargs):
        self.que.put({
            'func': task,
            'args': args,
            'kwargs': kwargs
        })
        self.task_count += 1

    def wait_all_task_done(self):
        while not self.que.empty():
            time.sleep(0.1)
        success_count = 0
        failed_count = 0
        copy_count = 0
        for thread in self.threads:
            while not thread.finished:
                time.sleep(0.1)
            success_count += thread.success_count
            failed_count += thread.failed_count
            copy_count += thread.copy_count
        self.alive = False
        logger.info('总任务数: {}, 成功: {}, 失败: {}'.format(self.task_count, success_count, failed_count))
        return copy_count


class Config(DefaultConfig):
    def __init__(self, **kwargs):
        self.Genernal = ConfigTemplate(
            source=None,
            target=None,
            thread_size=10,
            debug=False
        )
        super(Config, self).__init__(**kwargs)

    def on_finish(self):
        if self.Genernal.debug:
            logger.setLevel(logger.DEBUG)


class SyncTool(object):
    MAX_SIZE = 1024 * 1024

    def __init__(self, pool=None):
        self.pool = pool

    def _check_copy(self, source, target):
        if self.check_file_is_change(source, target):
            shutil.copy(source, target)
            logger.info('[拷贝] 从{}到{}'.format(source, target))
            return 1
        return 0

    def sync(self, source_path, target_path):
        rule = Rule(source_path, logger=logger)
        print('将要复制{}到{}?'.format(source_path, target_path))
        data = input('确定Y/N[N]')
        if data.upper() != 'Y':
            return 0

        def _sync(source, target):
            if not source or not target or not os.path.exists(source):
                return 0
            if os.path.isfile(source):
                if rule.check_is_ignore(source):
                    # print('[IgnoreFile] {}'.format(source))
                    return 0
                if self.pool is not None:
                    self.pool.add_task(self._check_copy, source, target)
                    return 0
                else:
                    return self._check_copy(source, target)
            else:
                if not os.path.exists(target):
                    os.makedirs(target)
                    logger.info('[创建文件夹] {}'.format(target))
                count = 0
                for item in os.listdir(source):
                    p = os.path.join(source, item)
                    if rule.check_is_ignore(p, item):
                        # print('[Ignore] {}'.format(p))
                        continue
                    count += _sync(os.path.join(source, item), os.path.join(target, item))
                return count

        count = _sync(source_path, target_path)
        if self.pool is not None:
            return self.pool.wait_all_task_done()
        else:
            return count

    def check_file_is_change(self, source, target):
        if os.path.exists(source):
            if not os.path.exists(target):
                return True
            source_hash = self.get_file_md5(source)
            target_hash = self.get_file_md5(target)
            return source_hash != target_hash
        else:
            return False

    def get_file_md5(self, file_path):
        if not os.path.isfile(file_path):
            return
        file_hash = hashlib.md5()
        size = os.stat(file_path)[stat.ST_SIZE]
        with open(file_path, 'rb') as f:
            if size < self.MAX_SIZE:
                file_hash.update(f.read())
            else:
                while True:
                    data = f.read(8096)
                    if not data:
                        break
                    file_hash.update(data)
            # print('[File] {}, size={}, md5={}'.format(file_path, size, file_hash.hexdigest()))
            return file_hash.hexdigest()


if __name__ == '__main__':
    config_file = os.path.join(os.getcwd(), 'config.ini') if hasattr(sys, 'frozen') \
            else os.path.join(os.getcwd(), 'spec', 'dist', 'config.ini')
    config = Config(config_file=config_file, config_type='ini', logger=logger)
    config.show()
    pool = ThreadPool(config.Genernal.thread_size)
    start = time.time()
    sync_tool = SyncTool(pool)
    count = sync_tool.sync(config.Genernal.source, config.Genernal.target)
    logger.info('复制文件数: {}, 用时: {}'.format(count, time.time() - start))
    input('输出回车退出')

