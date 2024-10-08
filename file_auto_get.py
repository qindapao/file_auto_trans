#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 执行机那边安装git bash,保证有sftp工具
import os
import hashlib
import subprocess
import time
import json
from datetime import datetime
import shutil
import sys
import paramiko
from colorama import Fore, Style, init

DM5_NUM = {}

# :TODO: 后面可能还需要处理同名但是目录不同的文件?(需求并不大)

with open('.\\get_file.json', 'r', encoding='utf-8') as my_file:
    JSON_INFO = json.load(my_file)

GREEN_PATH = JSON_INFO['GREEN_PATH']
LOCAL_DIR = JSON_INFO['LOCAL_DIR']
USER = JSON_INFO['USER']
PWD = JSON_INFO['PWD']

HOST_USER = JSON_INFO['HOST_USER']
HOST_PWD = JSON_INFO['HOST_PWD']
PUT_DIR_DICT = JSON_INFO['PUT_DIR_DICT']
HOST_PORT = JSON_INFO['HOST_PORT']
HOST_IP = JSON_INFO['HOST_IP']
if isinstance(HOST_IP, str):
    HOST_IP = [HOST_IP]

DEST_DIR = JSON_INFO['DEST_DIR']


def get_md5(single_file):
    with open(single_file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def mkdir_p(sftp, remote_directory):
    """Change to this directory, recursively making new folders if needed.
    Returns True if any folders were created."""
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory)  # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname)  # make parent directories
        sftp.mkdir(basename)  # sub-directory missing, so created it
        sftp.chdir(basename)
        return True

def remote_file(ip, local_f, remote_f, time_out, opo=None):
    ssh_c = paramiko.SSHClient()
    ssh_c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_c.connect(
        ip, username=HOST_USER, password=HOST_PWD, timeout=time_out,
        port=HOST_PORT)
    sftp = ssh_c.open_sftp()
    try:
        if opo == 'get':
            sftp.get(remote_f, local_f)
        elif opo == 'put':
            remote_dir = os.path.dirname(remote_f)
            try:
                sftp.stat(remote_dir)
            except IOError:
                mkdir_p(sftp, remote_dir)
            sftp.put(local_f, remote_f)
    except Exception:
        return False
    finally:
        sftp.close()
        ssh_c.close()
    return True


def delete_all_files_in_a_dir(delete_dir):
    if os.path.exists(delete_dir):
        for filename in os.listdir(delete_dir):
            file_path = os.path.join(delete_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        print("The directory does not exist")

def update_local_files(sleep_time):
    # 下载更新文件(多次循环保证文件取完)
    for _ in range(5):
        subprocess.check_output(
            [GREEN_PATH, '-l', LOCAL_DIR, '-u', USER, '-p', PWD],
            stderr=subprocess.STDOUT)
    # :TODO: 有什么更好的方法判断传送文件已经完成
    time.sleep(sleep_time)


def check_and_upload():
    # 第一次取文件时间长点
    update_local_files(10)
    while True:
        for sub_file in os.listdir(LOCAL_DIR):
            local_file = LOCAL_DIR + os.path.sep + sub_file
            md5_val = get_md5(local_file)
            spec_val = DM5_NUM.get(sub_file)
            if md5_val != spec_val:
                DM5_NUM.update({sub_file: md5_val})
                # sftp上传文件到环境中
                for host_ip in HOST_IP:
                    remote_file(
                            host_ip, local_file, PUT_DIR_DICT[sub_file], 20, 'put')
                    print(f"{Fore.GREEN}{datetime.now().strftime('%H:%M:%S %Y-%m-%d')}{Style.RESET_ALL} {PUT_DIR_DICT[sub_file]} {host_ip} updated")

        update_local_files(3)

if __name__ == '__main__':
    init()
    # 如果JSON_INFO中的DEST_DIR键不为空，那么获取一次绿传中的所有文件，
    # 然后重新填充JSON文件(PUT_DIR_DICT键)，
    # 并且删除DEST_DIR键，然后退出程序，等待下一次执行
    delete_all_files_in_a_dir(LOCAL_DIR)
    
    if DEST_DIR:
        if DEST_DIR.endswith('/'):
            DEST_DIR = DEST_DIR[:-1]

        print(f"DEST_DIR:{DEST_DIR}\n")

        for _ in range(5):
            subprocess.check_output(
                [GREEN_PATH, '-l', LOCAL_DIR, '-u', USER, '-p', PWD],
                stderr=subprocess.STDOUT)

        time.sleep(10)

        PUT_DIR_DICT = {}
        for sub_file in os.listdir(LOCAL_DIR):
            local_file = DEST_DIR + '/' + sub_file
            PUT_DIR_DICT[sub_file] = local_file

        JSON_INFO["DEST_DIR"] = ""
        JSON_INFO["PUT_DIR_DICT"] = PUT_DIR_DICT

        with open('.\\get_file.json', 'w', encoding='utf-8') as my_file:
            json.dump(JSON_INFO, my_file, indent=4)
        sys.exit(0)

    try:
        check_and_upload()
    except Exception as e:
        print(f"fatal err happen. {e}")
        time.sleep(10)


