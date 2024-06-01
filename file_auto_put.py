#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import subprocess
import time
import json
import os
from datetime import datetime


MD5_DICT = {}

with open('.\\put_file.json', 'r', encoding='utf-8') as my_file:
    JSON_INFO = json.load(my_file)

GREEN_PATH = JSON_INFO['GREEN_PATH']
FILE_LIST = JSON_INFO['FILE_LIST']
USER = JSON_INFO['USER']
PWD = JSON_INFO['PWD']


def get_all_md5():
    for path in FILE_LIST:
        if os.path.isdir(path):
            process_directory(path, is_just_record_md5=True)
        else:
            MD5_DICT[path] = get_md5(path)


def get_md5(single_file):
    with open(single_file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def upload_file(file_path):
    print(f"{file_path} put in {datetime.now()}")
    MD5_DICT[file_path] = get_md5(file_path)
    subprocess.check_output(
        [GREEN_PATH, '-r', file_path, '-u', USER, '-p', PWD],
        stderr=subprocess.STDOUT)

def process_directory(
        root_path, is_just_record_md5=False, is_force_update=False):
    for root, dirs, files in os.walk(root_path):
        # 首先处理所有文件
        for file in files:
            file_path = os.path.join(root, file)
            # 临时措施
            if '.git' in file_path:
                continue
            if not is_just_record_md5:
                if is_force_update or (
                        get_md5(file_path) != MD5_DICT[file_path]):
                    upload_file(file_path)
            MD5_DICT[file_path] = get_md5(file_path)


def check_and_upload(is_force_update=False):
    for val in FILE_LIST:
        if os.path.isdir(val):
            process_directory(
                    val,
                    is_just_record_md5=False,
                    is_force_update=is_force_update)
        else:
            if is_force_update or (get_md5(val) != MD5_DICT[val]):
                upload_file(val)
            MD5_DICT[val] = get_md5(val)


if __name__ == '__main__':
    get_all_md5()
    print(json.dumps(MD5_DICT, indent=4))
    check_and_upload(is_force_update=True)
    while True:
        check_and_upload(is_force_update=False)
        time.sleep(1)

