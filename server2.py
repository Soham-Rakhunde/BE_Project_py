from binascii import hexlify
import socket
import os
from _thread import *

mac_list = set()
ip_address = dict()
port_number = dict()

all_data = set()

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
ThreadCount = 0


try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')


ServerSideSocket.listen(5)
def multi_threaded_client(connection,address):
    try:
        connection.send(str.encode('!!Server is working!!'))
        uni_data = connection.recv(2048)
        uni_data = uni_data.decode('utf-8')
        all_data.add(uni_data)
        mac_data,ip_data,port_data = uni_data.split(" ")
        if(mac_data not in mac_list):
            mac_list.add(mac_data)
            ip_address[mac_data]=[ip_data]
            port_number[mac_data]=[port_data]
        else:
            ip_address[mac_data].append(ip_data)
            port_number[mac_data].append(port_data)

        while True:
            data = connection.recv(2048)
            data = data.decode('utf-8')
            response=''
            if not data:
                break
            if data=='1':       #all connected clients
                response = str(all_data)
            else:   #returns list and data is mac address
                if(data in mac_list):
                    response = ''              
                    for i in range(len(ip_address[data])):
                        if(i!=len(ip_address[data])-1):
                            response+=(ip_address[data][i]+' '+port_number[data][i]+',')
                        else:
                            response+=(ip_address[data][i]+' '+port_number[data][i])
                else:
                    response = 'wrong call'
            connection.sendall(str.encode(response))

    except ConnectionResetError:
        all_data.remove(uni_data)
        n = len(ip_address[mac_data])
        if(n==1):
            mac_list.remove(mac_data)
            ip_address.pop(mac_data)
            port_number.pop(mac_data)
        else:
            ip_address[mac_data].remove(ip_data)
            port_number[mac_data].remove(port_data)
        connection.close()


while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' +address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, address,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSideSocket.close()
