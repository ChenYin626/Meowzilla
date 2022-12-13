# coding=utf-8

import json
import logging
import os
import re
import sys
from functools import wraps
from hashlib import md5
from logging.handlers import TimedRotatingFileHandler

import time
from flask import Flask, request, jsonify, abort

from modules.servers import server
from modules.vsftpd import vsftpd

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

ACCOUNTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/accounts.json")

SESSION_IDS = {}

LOGIN_TIMEOUT = 60 * 60 * 24

logger = logging.getLogger("werkzeug")
handler = TimedRotatingFileHandler(filename="logs/main.log", when="D", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$")
logger.addHandler(handler)


# 权限验证
def permission(func):
    @wraps(func)
    def inner():
        session_id = request.headers.get("session_id", "")
        global SESSION_IDS
        if session_id not in SESSION_IDS:  # 是否存在会话信心
            return {"data": None, "status_code": "FORBIDDEN", "message": "username not login"}
        if int(time.time()) - SESSION_IDS.get(session_id).get("timestamp") > LOGIN_TIMEOUT:  # 是否会话仍有效
            SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
            return {"data": None, "status_code": "FORBIDDEN", "message": "username login timeout"}
        SESSION_IDS[session_id]["timestamp"] = int(time.time())  # 更新会话时间
        return func()

    return inner


# 登录
@app.route("/login", methods=["POST"])
def login():
    """用户登录"""
    username = request.form.get("username")
    password = request.form.get("password")
    if not os.path.exists(ACCOUNTS_FILE):  # 是否存在用户信息文件
        return {"data": None, "status_code": "NotFound", "message": "not found accounts file"}
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    usernames = [account["username"] for account in accounts]
    if username not in usernames:  # 是否用户已注册
        return {"data": None, "status_code": "NotFound", "message": "username is not exists"}

    for account in accounts:
        if account["username"] == username:
            if md5(username + password + "nervergiveup").hexdigest() != account["password"]:  # 是否用户名密码正确
                return {"data": None, "status_code": "Unauthorized", "message": "password is not correct"}
            session_id = md5((password + str(time.time()))).hexdigest()  # 生成会话ID
            global SESSION_IDS
            SESSION_IDS[session_id] = {"user_info": account, "timestamp": int(time.time())}  # 记录会话信息
            return {"data": {"session_id": session_id}, "status_code": "OK", "message": "login successfully"}


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route("/ip", methods=["POST"])
@permission
def get_ip():
    return server.get_ip()


@app.route("/server/cpu/about")
@permission
def get_cpu_info():
    return server.get_cpu_info()


@app.route("/server/cpu/percent")
@permission
def get_cpu_percent():
    return server.get_cpu_percent()


@app.route("/server/memory")
@permission
def get_memory():
    return server.get_memory()


@app.route("/server/disks")
@permission
def get_disks():
    return server.get_disks()


@app.route("/server/disk_io_counters")
@permission
def get_disk_io_counters():
    return server.get_disk_io_counters()


@app.route("/server/net_io_counters")
@permission
def get_network_io_counters():
    return server.get_net_io_counters()


@app.route("/server/net_connections", methods=["POST"])
@permission
def get_net_connections():
    if request.json and 'kind' in request.json:
        return server.get_net_connections(request.json["kind"])
    else:
        return jsonify({"error": "title is required"}), 400


@app.route("/server/boot_time", methods=["GET"])
# @permission
def get_boot_time():
    return server.get_boot_time()


@app.route("/hello/tasks", methods=['POST'])
@permission
def create_task():
    if not request.json or 'title' not in request.json:
        abort(400)
    else:
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'done': False
        }
        tasks.append(task)
        return jsonify({'task': task}), 201


@app.route("/vsftpd/userlist")
@permission
def get_vsftpd_users():
    return jsonify(vsftpd.get_virtual_user())


@app.route("/vsftpd/start")
@permission
def init_vsftpd():
    if vsftpd.init_vsftpd():
        return jsonify({"start_status": "ok"})
    else:
        return jsonify({"start_status": "error"})


@app.route("/vsftpd/status")
@permission
def status_vsftpd():
    return jsonify({"vsftpd_status": vsftpd.status_vsftpd()})


@app.route("/vsftpd/cmd", methods=["POST"])
@permission
def cmd_vsftpd():
    if request.json and 'cmd' in request.json:
        value = request.json.get("cmd", "")
        if value in ["start", "stop", "restart", "enable", "disable", "status"]:
            return jsonify(vsftpd.cmd_vsftpd(value))
        else:
            return jsonify({"error": "cmd is error"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
