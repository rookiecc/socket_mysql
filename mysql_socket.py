import socket
import struct

client = socket.create_connection(('127.0.0.1',3306))

recv = client.recv(1024)[4:]

print(recv)

len = 0
len = len + 1
protocol_version = struct.unpack('b',recv[0:len])[0]

print("协议版本:%s" % protocol_version)

position = recv.find(b'\x00')
data_version= recv[len:position]
gap = position - len
fmt = str(gap)+'s'
data_version  = struct.unpack(fmt,data_version)
print("数据库版本:%s" % (data_version[0]).decode())
thread_id = recv[position+1:position+5]
print("线程ID: %s" % struct.unpack('L',thread_id))
position = position + 5
randcode = recv[position:position+8]
print("挑战码: %s" % struct.unpack('8s',randcode))
position = position+8
sever_flag = recv[position:position+2]
print("服务器标识: %s" % struct.unpack('2s',sever_flag))
# print("服务器标识: %s" % bin(struct.unpack('H',sever_flag)[0]))
position = position + 3
character = recv[position:position+1]
print("字符集: %s" % struct.unpack('b',character))
position = position + 1
server_status = recv[position:position+1]
print("服务器状态: %s" % struct.unpack('s',server_status))
position = position + 1
sever_flag_upper = recv[position:position+2]
print("服务器状态(高): %s" % struct.unpack('2s',sever_flag_upper))
# print("服务器状态(高): %s" % bin(struct.unpack('H',sever_flag_upper)[0]))
position = position + 14

recv = recv[position:]
position =  recv.find(b'\x00')
salt_length = position
salt = recv[:position]
fmt = str(position) + 's'
print("salt : %s" % struct.unpack(fmt,salt))

recv = recv[position+1:]
position =  recv.find(b'\x00')
password_type = recv[:position]
fmt = str(position) + 's'
print("密码类型 : %s" % struct.unpack(fmt,password_type))
fmt = str(salt_length+8) + 's'
print("seed： %s" %   struct.unpack(fmt,randcode + salt) )

