# -*- coding: utf-8 -*-
"""
@Author         ：Cat
@Date           : 2022年 11月 05日
@Introduction   ：A Lazy Cat
"""
import os

import subprocess
import shlex
from modules.Log.MyLogging import MyLogging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
logger = MyLogging("vsftpd.log")

'''
使用yum安装vsftpd
'''


def install_vsftpd():
    cmd = "yum install vsftpd -y"
    cmd = shlex.split(cmd)
    logger.write_debug_logger("开始安装vsftpd")
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("安装vsftpd成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("安装vsftpd失败" + str(e))
        return False


def remove_vsftpd():
    cmd = "yum remove vsftpd -y"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("卸载vsftpd成功")
    except subprocess.CalledProcessError as e:
        logger.write_debug_logger("卸载vsftpd失败" + str(e))
        return False
    cmd = "userdel -rf virtualuser"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("删除虚拟用户成功")

    except subprocess.CalledProcessError as e:
        logger.write_debug_logger("删除虚拟用户失败" + str(e))
    finally:
        return True


def check_vsftpd():
    cmd = "rpm -q vsftpd"
    cmd = shlex.split(cmd)
    try:
        p = subprocess.Popen(cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err, = p.communicate()
        if len(out.split()) > 0:
            logger.write_debug_logger("vsftpd已经安装")
            return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("检查vsftpd失败")
        return False


def update_vsftpd_user():
    cmd = "db_load -T -t hash -f /root/virtual /etc/vsftpd/virtual.db"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("创建虚拟用户口令库文件成功")
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("创建虚拟用户口令库文件失败" + str(e))
        return False
    output = subprocess.check_output("chmod 600 /etc/vsftpd/virtual.db", shell=True)


def get_virtual_user():
    user_dic = {}
    with open("/root/virtual", "r") as f:
        lines = f.readlines()
        if len(lines) % 2 != 0:
            logger.write_error_logger("虚拟用户配置文件错误")
            return False
        for i in range(0, len(lines), 2):
            user_dic[lines[i].strip()] = lines[i + 1].strip()

    return user_dic


def init_vsftpd():
    install_vsftpd()
    # 检查vsftpd是否安装
    if check_vsftpd():
        logger.write_debug_logger("开始初始化vsftpd")
        cmd = "cp /etc/vsftpd/vsftpd.conf /etc/vsftpd/vsftpd.conf.bak"
        cmd = shlex.split(cmd)
        try:
            subprocess.check_output(cmd, shell=False)
            logger.write_debug_logger("备份vsftpd配置文件成功")
        except subprocess.CalledProcessError as e:
            logger.write_error_logger("备份vsftpd配置文件失败" + str(e))
            return False
        cmd = "adduser -d /home/ftpuser virtualuser -s /sbin/nologin"
        cmd = shlex.split(cmd)
        try:
            subprocess.check_output(cmd, shell=False)
            logger.write_debug_logger("adduser -d /home/ftpuser virtualuser命令执行成功")
        except subprocess.CalledProcessError as e:
            logger.write_error_logger("adduser -d /home/ftpuser virtualuser命令执行失败" + str(e))
            return False
        # os.chmod("/home/ftpuser", 700)
        output = subprocess.check_output("chmod 700 /home/ftpuser", shell=True)
        subprocess.check_output("chown -R virtualuser:virtualuser /home/ftpuser", shell=True)
        if virtual_user(init=True):
            try:
                with open("/etc/pam.d/vsftpd.vu", "w") as f:
                    f.write("auth required /usr/lib64/security/pam_userdb.so db=/etc/vsftpd/virtual\n")
                    f.write("account required /usr/lib64/security/pam_userdb.so db=/etc/vsftpd/virtual\n")
                logger.write_debug_logger("创建/etc/pam.d/vsftpd.vu文件成功")
            except Exception as e:
                logger.write_error_logger("创建/etc/pam.d/vsftpd.vu文件失败" + str(e))
                return False
            update_vsftpd_user()

            # 配置vsftpd.conf
            if config_vsftpd():
                logger.write_debug_logger("配置vsftpd.conf成功")
                logger.write_debug_logger("用户名：cat")
                logger.write_debug_logger("密码：catpasswd")
                logger.write_debug_logger("请使用ftp客户端连接服务器")
                return True
    else:
        logger.write_debug_logger("vsftpd未安装")
        return False


# 创建/root/virtual文件,存放虚拟用户信息
def virtual_user(init=False, mode=None, user=None):
    if init:
        try:
            with open("/root/virtual", "w") as f:
                f.write("cat\n")
                f.write("catpasswd\n")
            logger.write_debug_logger("初始化虚拟用户成功")
            update_vsftpd_user()
            user_single_config({"cat": "catpasswd"})
            return True
        except Exception as e:
            logger.write_error_logger("初始化虚拟用户失败" + str(e))
            return False

    user_dic = get_virtual_user()

    if mode == "add":
        for name, passwd in user.items():
            user_dic[name] = passwd
    if mode == "delete":
        for name, passwd in user.items():
            user_dic.pop(name)
    # 创建虚拟用户口令库文件
    with open("/root/virtual", "w") as f:
        for name, passwd in user_dic.items():
            f.write(name + "\n")
            f.write(passwd + "\n")
    update_vsftpd_user()
    user_single_config(user_dic)


def user_single_config(user_dic):
    for name, passwd in user_dic.items():
        if os.path.exists("/home/ftpuser/" + name + "/rootdir"):
            pass
        else:
            os.makedirs("/home/ftpuser/" + name + "/rootdir")
        os.chmod("/home/ftpuser/" + name, 0o500)
        with open("/etc/vsftpd/vsftpd_user/" + name, "w") as f:
            f.write("local_root=/home/ftpuser/" + name + "\n")
            f.write("anon_world_readable_only=NO\n")
            f.write("anon_upload_enable=YES\n")
            f.write("anon_mkdir_write_enable=YES\n")
            f.write("anon_other_write_enable=YES\n")
    subprocess.check_output("chown -R virtualuser:virtualuser /home/ftpuser", shell=True)


'''
配置vsftpd使用虚拟用户的方式进行配置
'''


def config_vsftpd():
    dict_config = {
        "anonymous_enable": "NO",
        "local_enable": "YES",
        "write_enable": "YES",
        "anon_upload_enable": "NO",
        "anon_mkdir_write_enable": "NO",
        "anon_other_write_enable": "NO",
        "one_process_model": "NO",
        "chroot_local_user": "YES",
        "ftpd_banner": "Welcome to use FTP service.",
        "guest_enable": "YES",
        "guest_username": "virtualuser",
        "local_umask": "022",
        "dirmessage_enable": "YES",
        "xferlog_enable": "YES",
        "connect_from_port_20": "YES",
        "xferlog_std_format": "YES",
        "listen": "YES",
        "pam_service_name": "vsftpd.vu",
        "userlist_enable": "YES",
        "tcp_wrappers": "YES",
        "allow_writeable_chroot": "YES",
        "pasv_enable": "YES",
        "pasv_min_port": "40000",
        "pasv_max_port": "50000",
        "pasv_promiscuous": "YES",
        "user_config_dir": "/etc/vsftpd/vsftpd_user",
        "virtual_use_local_privs": "YES",
    }
    with open("/etc/vsftpd/vsftpd.conf", "w") as f:
        for key in dict_config:
            f.write(key + "=" + dict_config[key] + "\n")
    if not os.path.exists("/etc/vsftpd/vsftpd_user"):
        os.makedirs("/etc/vsftpd/vsftpd_user")
    logger.write_debug_logger("vsftpd配置文件初始化成功")
    if restart_vsftpd():
        return True
    else:
        return False


def start_vsftpd():
    cmd = "systemctl start vsftpd"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("启动vsftpd服务成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("启动vsftpd服务失败" + str(e))
        return False


def stop_vsftpd():
    cmd = "systemctl stop vsftpd"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("启动vsftpd服务成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("启动vsftpd服务失败" + str(e))
        return False


def disable_vsftpd():
    cmd = "systemctl disable vsftpd"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("启动vsftpd服务成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("启动vsftpd服务失败" + str(e))
        return False


def enable_vsftpd():
    cmd = "systemctl enable vsftpd"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("设置vsftpd开机启动成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("设置vsftpd开机启动失败" + str(e))
        return False


def restart_vsftpd():
    cmd = "systemctl restart vsftpd"
    cmd = shlex.split(cmd)
    try:
        subprocess.check_output(cmd, shell=False)
        logger.write_debug_logger("重启vsftpd服务成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("重启vsftpd服务失败" + str(e))
        return False


def status_vsftpd():
    cmd = "systemctl status vsftpd"
    cmd = shlex.split(cmd)
    try:
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err, = p.communicate()
        if "Active: active (running)" in out:
            logger.write_debug_logger("vsftpd服务状态Active: active (running)")
            return "running"
        if "Active: inactive (dead)" in out:
            logger.write_error_logger("vsftpd服务状态:Active: inactive (dead)")
            return "dead"
        if "Active: failed" in out:
            logger.write_warning_logger("vsftpd服务状态:Active: failed")
            return "failed"
    except subprocess.CalledProcessError as e:
        logger.write_error_logger("vsftpd服务状态异常" + str(e))
        return "cmd_error"
    # print subprocess.call(["yum"])
    # print os.path.exists("/etc/vsftpd/vsftpd.conf")
    # install_vsftpd()
    #
    # check_vsftpd()


def cmd_vsftpd(value=""):
    if value == "start":
        if start_vsftpd():
            return {"cmd": "start", "status": "ok"}
        else:
            return {"cmd": "start", "status": "error"}
    if value == "stop":
        if stop_vsftpd():
            return {"cmd": "stop", "status": "ok"}
        else:
            return {"cmd": "stop", "status": "error"}
    if value == "restart":
        if restart_vsftpd():
            return {"cmd": "restart", "status": "ok"}
        else:
            return {"cmd": "restart", "status": "error"}
    if value == "status":
        return {"cmd": "status", "status": status_vsftpd()}
    if value == "enable":
        if enable_vsftpd():
            return {"cmd": "enable", "status": "ok"}
        else:
            return {"cmd": "enable", "status": "error"}
    if value == "disable":
        if disable_vsftpd():
            return {"cmd": "disable", "status": "ok"}
        else:
            return {"cmd": "disable", "status": "error"}


if __name__ == '__main__':
    # remove_vsftpd()
    # init_vsftpd()
    print get_virtual_user()
    virtual_user(init=False, mode="add", user={"tom": "abc"})
    print get_virtual_user()
