#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse

ftp_param = {}
upload_params = []
dom = parse("./config.xml")
# 获取文件元素对象
document = dom.documentElement
ftp_server = document.getElementsByTagName("ftp_server")[0]
ftp_param["host"] = ftp_server.getElementsByTagName("host")[0].childNodes[0].data
ftp_param["port"] = int(ftp_server.getElementsByTagName("port")[0].childNodes[0].data)
ftp_param["user"] = ftp_server.getElementsByTagName("user")[0].childNodes[0].data
ftp_param["pwd"] = ftp_server.getElementsByTagName("password")[0].childNodes[0].data

transforms = document.getElementsByTagName("transforms")[0].getElementsByTagName("transform")
for tran in transforms:
    tran_dist = {"local_dir": tran.getElementsByTagName("local")[0].childNodes[0].data,
                 "server_dir": tran.getElementsByTagName("server")[0].childNodes[0].data}
    upload_params.append(tran_dist)


# # 文件服务器参数
# ftp_param = {
#     "host": "127.0.0.1",
#     "port": 21,
#     "user": "user",
#     "pwd": "password"
# }
#
# # 配置需要上传的文件目录消息
# # 可以配置多组目录
# upload_params = [
#     {
#         "local_dir": "D:\\May\\",
#         "server_dir": "/gdata/"
#     },
#     {
#         "local_dir": "D:\\gdata\\",
#         "server_dir": "/gdata/"
#     }
# ]