# -*- coding: utf-8 -*-
"""
@Author         ：Cat
@Date           : 2022年 11月 08日
@Introduction   ：A Lazy Cat
"""
import os
import shlex
import subprocess
import sys
from modules.Log.MyLogging import MyLogging

reload(sys)
sys.setdefaultencoding('utf-8')
logger = MyLogging("nginx")

'''
判断/Meowzilla/tmp目录下是否已经缓存了nginx源文件，如果没有就从nginx.org下载。然后解压到/Meowzilla/tmp目录下

'''


def get_source_file():
    def exit_status():
        if not os.path.exists("/Meowzilla/tmp/nginx-1.22.1.tar.gz"):
            command = "curl -o /Meowzilla/tmp/nginx-1.22.1.tar.gz https://nginx.org/download/nginx-1.22.1.tar.gz"
            command = shlex.split(command)
            popen = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error, = popen.communicate()
            print output, error
            if popen.returncode != 0:
                print "download error"
                return False
            else:
                return True
        else:
            return True

    if exit_status():
        cmd = "tar -zxvf /Meowzilla/tmp/nginx-1.22.1.tar.gz -C /Meowzilla/tmp/"
        cmd = shlex.split(cmd)
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            logger.write_error_logger(err)
            return False
        else:
            logger.write_info_logger(out)
            return True


def install_nginx():
    cmd = "./configure --prefix=/Meowzilla/application_files " \
          "--user=nginx " \
          "--group=nginx " \
          "--with-compat " \
          "--with-debug " \
          "--with-file-aio " \
          "--with-google_perftools_module " \
          "--with-http_addition_module " \
          "--with-http_auth_request_module " \
          "--with-http_dav_module " \
          "--with-http_degradation_module " \
          "--with-http_flv_module " \
          "--with-http_gunzip_module " \
          "--with-http_gzip_static_module " \
          "--with-http_image_filter_module=dynamic " \
          "--with-http_mp4_module " \
          "--with-http_perl_module=dynamic " \
          "--with-http_random_index_module " \
          "--with-http_realip_module " \
          "--with-http_secure_link_module " \
          "--with-http_slice_module " \
          "--with-http_ssl_module " \
          "--with-http_stub_status_module " \
          "--with-http_sub_module " \
          "--with-http_v2_module " \
          "--with-http_xslt_module=dynamic " \
          "--with-mail=dynamic " \
          "-with-mail_ssl_module " \
          "--with-pcre " \
          "--with-pcre-jit " \
          "--with-stream=dynamic " \
          "--with-stream_ssl_module " \
          "--with-stream_ssl_preread_module " \
          "--with-threads " \
          "--with-cc-opt='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong " \
          "--param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC' " \
          "--with-ld-opt='-Wl,-z,relro -Wl,-z,now -pie'"
    popen = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = popen.communicate()
    if popen.returncode != 0:
        logger.write_error_logger(err)
        return False
    else:
        logger.write_info_logger(out)
        return True
