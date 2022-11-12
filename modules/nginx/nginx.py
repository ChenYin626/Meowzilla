# -*- coding: utf-8 -*-
"""
@Author         ：Cat
@Date           : 2022年 11月 08日
@Introduction   ：A Lazy Cat
"""
import shlex
import subprocess
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def install_nginx():
    cmd = "yum install -y nginx"
    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err, = p.communicate()
    print out,err
