# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 22:34:31 2019

@author: Administrator
"""

import socket
import struct
import binascii
import util.commutil
import sha1

client = socket.create_connection(('127.0.0.1',3306))

data = client.recv(1024)

sendBytes = []

#print('获取的原始数据: %s ' % data)
port = data[4:5] # 协议版本
data_version  = data[5:11] #数据库版本
tid = data[12:13]#服务器线程ID
randCode = data[16:24]#随机码
salt = data[43:55]
print('协议版本:%s' % struct.unpack('b',port))
print('数据库版本: %s' % data_version.decode())
print('线程ID %s' % int(binascii.hexlify(tid),16))
print('随机码 %s' % randCode)
print('salt %s' % salt)
seed = (randCode.decode()+ salt.decode()).encode()
print('seed %s' % seed)

#seed = b'4MiImjN%'+b'lquxyvevA!"&'
#发送数据
packetId = 0
clientFlags = util.commutil.getClientCapabilities()
maxPacketSize = 1024 * 1024 * 16    
user = b'root'
password = sha1.getpass('123456'.encode('utf-8'),seed)
database = b'test'

charset_id = 33
data_init = struct.pack('<iIB23s', clientFlags, maxPacketSize, charset_id, b'')
data = data_init + user + b'\0'
data += util.commutil.lenenc_int(len(password)) + password
data +=  database +b'\0'

senddata = util.commutil.pack_int24(len(data)) + util.commutil.int2byte(1) + data

client.sendall(senddata)

data = client.recv(1024)
response_code = data[5:]
if response_code[0] == 0x00:
    print("链接成功")
    #改变数据库
    code = 2
    commd = b'example'
    fmt = '<ib'
    ss = struct.pack(fmt,len(commd)+1,code)
    ss = ss + commd
    print(ss)
    client.sendall(ss)
    data = client.recv(1024)
    response_code = data[5:]
    if response_code[0] == 0x00:
        print("OK包")
        code = 3
        commd = b'select * from article'
        fmt = '<ib'
        ss = struct.pack(fmt,len(commd)+1,code)
        ss = ss +  commd
        client.sendall(ss)
     
        data = client.recv(maxPacketSize)
        
        number_filed = data[4:5]
        start_pgk_position = 5
        print("获取字段数量 %s" % struct.unpack('b',number_filed))
        n_f = struct.unpack('b',number_filed)[0]
        for i in range(1,n_f+1):
            print("获取第%s字段信息" % i)
            end_pgk_position = start_pgk_position + 3 #int<3>获取数据长度
            pgk_size = struct.unpack('3b',data[start_pgk_position:end_pgk_position])[0]
            print("包长度: %s " % (pgk_size))
            pgk_data = data[start_pgk_position:start_pgk_position+4+pgk_size][5:] #获取包数据跳过前4个字节
            print("包数据: %s" % pgk_data)
            b_field_def = pgk_data[:3]
            field_def = struct.unpack('3s',b_field_def)
            print("def : %s" % field_def[0].decode())
            databasename_size = struct.unpack('!B',pgk_data[3:4])
            print('数据库名称长度: %s' % databasename_size)
            database_name = pgk_data[4:4+databasename_size[0]]
            print('数据库名称: %s' % database_name.decode())
            start_position = 4+databasename_size[0]
            tablenname_size = struct.unpack('!B',pgk_data[start_position:start_position+1])
            end_position = start_position + 1 + tablenname_size[0]
            print('表名称长度(别名): %s' % tablenname_size)
            database_name = pgk_data[start_position+1:end_position]
            print('表名称(别名): %s' % database_name.decode())
            start_position = end_position
            orignal_tablenname_size = struct.unpack('!B',pgk_data[start_position:start_position+1])
            print('表名称长度: %s' % orignal_tablenname_size[0])
            end_position = end_position + 1 + orignal_tablenname_size[0]
            origdatabase_name = pgk_data[start_position+1:end_position]
            print('表名称: %s' % origdatabase_name.decode())
            start_position = end_position
            alias_filed_size = struct.unpack('!B',pgk_data[start_position:start_position+1])
            print('字段长度 (别名): %s' % alias_filed_size)
            end_position = end_position + 1 + alias_filed_size[0]
            alias_field_name = pgk_data[start_position+1:end_position]
            print('字段名称（别名): %s' % alias_field_name.decode())
            start_position = end_position
            filed_size = struct.unpack('!B',pgk_data[start_position:start_position+1])
            print('字段长度: %s' % filed_size[0])
            end_position = end_position + 1 + filed_size[0]
            field_name = pgk_data[start_position+1:end_position]
            print('字段名称 : %s' % field_name.decode())
            
            start_pgk_position = end_pgk_position + pgk_size +1 #计算下一个包的开始位置
        print(start_pgk_position)
        end_pgk_position = start_pgk_position + 3
        eof_size = struct.unpack('!3b',data[start_pgk_position:end_pgk_position])
        print('eof_size 长度: %s ' % eof_size[0])
        end_pgk_position = start_pgk_position + eof_size[0]
        eof_data = struct.unpack('!b',data[start_pgk_position+4:end_pgk_position])
        if -2 == eof_data[0]:
            start_pgk_position = start_pgk_position + 4 + eof_size[0]
            i = 1
            while True:
                print("获取第%s条数据信息" % i)
                end_pgk_position = start_pgk_position + 3 #int<3>获取数据长度
                pgk_size = struct.unpack('3b',data[start_pgk_position:end_pgk_position])[0]
                print(">>包长度: %s " % (pgk_size))
                pgk_data = data[start_pgk_position:start_pgk_position+4+pgk_size] #获取包数据跳过前4个字节
                print(">>包数据: %s" % pgk_data)
                eof_data = struct.unpack('!b',pgk_data[4:5])
                if -2 == eof_data[0]:
                    break
                start_pgk_position = end_pgk_position + pgk_size +1 #计算下一个包的开始位置
                i = i + 1
                
    
    
