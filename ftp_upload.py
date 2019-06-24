#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import time
from ftplib import FTP
from logging.handlers import TimedRotatingFileHandler
from upload_conf import ftp_param, upload_params
import sys

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
if not os.path.exists("logs"):
    os.mkdir("logs")
handler = TimedRotatingFileHandler(filename="logs/upload.log",
                                   when="d",
                                   interval=1,
                                   backupCount=90)
handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s'))
logger.addHandler(handler)

upload_successed = 0
upload_failed = 0
upload_exist = 0
file_del = 0


def __ftp_upload(ftp, local, remote, is_del=False):
    global upload_successed
    global upload_failed
    global upload_exist
    if os.path.isdir(local):
        for f in os.listdir(local):
            if os.path.isdir(local + f):
                try:
                    ftp.cwd(remote + f)
                except:
                    logging.info("[创建远程目录]:" + remote + f)
                    ftp.mkd(remote + f)
                logging.info("[上传本地目录]:" + local + f)
                __ftp_upload(ftp, local + f + '/', remote + f + '/', is_del)
            else:
                try:
                    __do_upload_file(f, ftp, is_del, local, remote)
                except Exception as e:
                    logging.error("上传文件失败, " + local + f)
                    logging.error(e)
                    logging.exception(e)
                    upload_failed += 1
    else:
        logging.error("配置有误." + local + "不是一个目录")


def __do_upload_file(f, ftp, is_del, local, remote):
    global upload_successed, upload_failed, file_del
    logging.info("[本地文件]:" + local + f)
    logging.info("[远程文件]:" + remote + f)
    fp = open(local + f, 'rb')
    if __check_need_to_upload(ftp, local + f, remote + f):
        try:
            ret = ftp.storbinary('STOR ' + remote + f, fp, 4096)
            server_size = ftp.size(remote + f)
            local_size = os.path.getsize(local + f)
            logging.info("server_size=" + str(server_size) + ", local_size=" + str(local_size))
            logging.info("ret=" + ret)
            if ret is not None and ret.startswith("226") and local_size == server_size:
                logging.info("[上传文件成功]:" + ret)
                upload_successed += 1
        except Exception as e:
            logging.error("上传文件失败, " + local + f)
            logging.error(e)
            logging.exception(e)
            upload_failed += 1
        fp.close()
    else:
        # 服务端文件已经存在，判断判断是否需要删除。
        logging.warn("[远程文件以已经存在，无需上传]: " + remote + f)
        # 文件存在时间
        file_exist_time = long(time.time()) - long(os.path.getsize(local + f))
        # 文件存在时间超过7天进行删除。
        if is_del and file_exist_time > 3600 * 24 * 7:
            logging.info("删除本地文件:" + local + f)
            # os.remove(local + f)
            file_del += 1


def __check_need_to_upload(ftp, local_file, remote_file):
    try:
        local_size = os.path.getsize(local_file)
        r_files = ftp.size(remote_file)
        if r_files >= local_size:
            # 当服务端文件比本地大的时候，不需要上传。其他情况都上传
            return False
    except :
        pass
    return True


def ftp_upload(host, port, username, password, local, remote, is_del=False):
    ftp = FTP()
    try:
        ftp.connect(host, port)
        ftp.login(username, password)
    except Exception as e:
        logging.error("连接远程服务器失败.")
        logging.error(e)
        logging.exception(e)
        return False
    try:
        __ftp_upload(ftp, local, remote, is_del)
    except Exception as e:
        logging.error("上传目录失败: 本地目录=" + local + ", 远程目录=" + remote)
        logging.error(e)
        logging.exception(e)
    ftp.close()
    return True


if __name__ == '__main__':
    logging.info("=============================================================")
    logging.info("启动程序")
    for info in upload_params:
        logging.info("开始上传,本地目录 = " + info['local_dir'] + ", 远程目录 = " + info['server_dir'])
        ftp_upload(ftp_param['host'],
                   ftp_param['port'],
                   ftp_param['user'],
                   ftp_param['pwd'],
                   info['local_dir'],
                   info['server_dir'],
                   True)
        logging.info("----------------------分割线-------------------------------")
    logging.info("上传成功文件数:" + str(upload_successed))
    logging.info("上传失败文件数:" + str(upload_failed))
    logging.info("已经存在文件数:" + str(upload_exist))
    logging.info("本次删除文件数:" + str(file_del))
    logging.info("结束程序")
