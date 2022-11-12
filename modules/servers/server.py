# -*- coding: utf-8 -*-
"""
@Author         ：Cat
@Date           : 2022年 11月 02日
@Introduction   ：A Lazy Cat
"""
import os

import time
from flask import Flask, request, jsonify, abort
import psutil
from psutil._common import bytes2human


def get_human_str(ma, bytes_to_human=False):
    to_dict = {}
    if bytes_to_human:
        for k, v in ma._asdict().items():
            to_dict[k] = bytes2human(v)
        return to_dict
    else:
        for k, v in ma._asdict().items():
            to_dict[k] = v
        return to_dict


def get_ip():
    return request.remote_addr


def get_cpu_info():
    logical_count = psutil.cpu_count()
    count = psutil.cpu_count(logical=False)
    return jsonify({"logical_count": logical_count, "count": count})


'''
获取cpu使用率,返回一个列表，每个元素代表一个cpu的使用率
cpu_percent:cpu每个核的使用率
avg_cpu_percent:cpu总体平均使用率
avg_cpu_times_percent:cpu每个核的性能参数
cpu_times_percent:cpu总体的性能参数
'''


def get_cpu_percent():
    cpu_percent = psutil.cpu_percent(interval=0.5, percpu=True)
    avg_cpu_percent = psutil.cpu_percent(interval=None, percpu=False)
    cpu_times_percent = psutil.cpu_times_percent(interval=None, percpu=False)
    avg_cpu_times_percent = psutil.cpu_times_percent(interval=None, percpu=True)
    b = {}
    for i in range(len(avg_cpu_times_percent)):
        b[i] = get_human_str(avg_cpu_times_percent[i])
    ret_str = {"percent": cpu_percent, "avg_cpu_percent": avg_cpu_percent,
               "cpu_times_percent": get_human_str(cpu_times_percent),
               "avg_cpu_times_percent": b}
    return jsonify(ret_str)


''' 
    total:总物理内存
    available:可用内存，available ～free + buffers + cached
    percent:使用率： percent = (total - available) / total * 100
    used：使用的内存： used  =  total - free - buffers - cache
    free：完全没用使用内存
    active：最近被访问的内存
    inactive：长时间未被访问的内存
    buffers：缓存
    cached：缓存
    slab：内核数据结构缓存的内存
'''


def get_memory():
    memory = get_human_str(psutil.virtual_memory(), True)
    memory['percent'] = memory['percent'].replace('B', "%")
    swap_memory = get_human_str(psutil.swap_memory(), True)
    swap_memory['percent'] = swap_memory['percent'].replace('B', "%")
    return jsonify({"memory": memory, "swap_memory": swap_memory})


'''
device：设备路径（例如"/dev/hda1"）。在 Windows 上，这是驱动器号（例如"C:\\"）。
mountpoint：挂载点路径（例如"/"）。在 Windows 上，这是驱动器号（例如"C:\\"）。
fstype：分区文件系统（例如"ext3"在 UNIX 或"NTFS" Windows 上）。
opts：以逗号分隔的字符串，指示驱动器/分区的不同挂载选项。平台相关。
maxfile：文件名可以具有的最大长度。
maxpath：路径名（目录名 + 基本文件名）可以具有的最大长度。
'''


def get_disks():
    key = ["Device", "Total", "Used", "Free", "Use ", "Type",
           "Mount"]
    disks = []
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        usage = psutil.disk_usage(part.mountpoint)
        disk = {}
        for i in key:
            if i == "Device":
                disk[i] = part.device
            elif i == "Total":
                disk[i] = bytes2human(usage.total)
            elif i == "Used":
                disk[i] = bytes2human(usage.used)
            elif i == "Free":
                disk[i] = bytes2human(usage.free)
            elif i == "Use ":
                disk[i] = str(usage.percent) + "%"
            elif i == "Type":
                disk[i] = part.fstype
            elif i == "Mount":
                disk[i] = part.mountpoint
        disks.append(disk)
    return jsonify(disks)


'''
获取磁盘实时写入数据
'''


def get_disk_io_counters():
    counters = psutil.disk_io_counters(perdisk=False, nowrap=True)
    time.sleep(1)
    counters2 = psutil.disk_io_counters(perdisk=False, nowrap=True)
    read_bytes = counters2.read_bytes - counters.read_bytes
    write_bytes = counters2.write_bytes - counters.write_bytes
    return jsonify({"read_bytes_speed": bytes2human(read_bytes) + "/s",
                    "write_bytes_speed": bytes2human(write_bytes) + "/s"})


'''
获取网络实时数据
'''


def get_net_io_counters():
    counters = psutil.net_io_counters(pernic=False, nowrap=True)
    time.sleep(0.5)
    counters2 = psutil.net_io_counters(pernic=False, nowrap=True)
    bytes_sent = counters2.bytes_sent - counters.bytes_sent
    bytes_recv = counters2.bytes_recv - counters.bytes_recv
    return jsonify({"bytes_sent_speed": bytes2human(bytes_sent * 2) + "/s",
                    "bytes_recv_speed": bytes2human(bytes_recv * 2) + "/s"})


def get_net_connections(my_choice="inet"):
    if my_choice != "inet":
        choice = ["inet", "inet4", "inet6", "tcp", "tcp4", "tcp6", "udp", "udp4", "udp6", "unix"]
        if my_choice in choice:
            connections = psutil.net_connections(kind=my_choice)
            return jsonify(connections)
        else:
            return jsonify({"error": "参数错误"})
    else:
        connections = psutil.net_connections(kind=my_choice)
        return jsonify(connections)
