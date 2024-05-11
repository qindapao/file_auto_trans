#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import shutil
import os


def file_remove(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def dir_remove(dir_name):
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)


def del_and_clear(exe_file):
    dir_remove('build')
    dir_remove('__pycache__')
    shutil.copy(f'.\\dist\\{exe_file}', f'.\\exe\\{exe_file}')
    dir_remove('dist')
    for sub_file in os.listdir('.'):
        if sub_file.endswith('spec'):
            file_remove(sub_file)


def auto_pack():
    file_remove('.\\exe\\file_auto_get.exe')
    file_remove('.\\exe\\file_auto_put.exe')
    subprocess.check_output(['pyinstaller', '-F', 'file_auto_put.py'],
                            stderr=subprocess.STDOUT)
    del_and_clear('file_auto_put.exe')
    subprocess.check_output(['pyinstaller', '-F', 'file_auto_get.py'],
                            stderr=subprocess.STDOUT)
    del_and_clear('file_auto_get.exe')


if __name__ == '__main__':
    auto_pack()

