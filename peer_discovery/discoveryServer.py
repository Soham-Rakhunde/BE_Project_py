from binascii import hexlify
import socket
import os,json,sys
from _thread import *

mac_list = set()
ip_address = dict()
port_number = dict()
all_data = set()

ServerSideSocket = socket.socket()
host = '0.0.0.0'
port = 11100
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
        uni_data_ = connection.recv(2048)
        uni_data_ = uni_data_.decode('utf-8')
        all_data.add(uni_data_)
        uni_data = json.loads(uni_data_)
        mac_data = uni_data['mac']
        ip_data = uni_data['ip']
        port_data = uni_data['port']
        
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
                raise ConnectionResetError
                break
            if data=='1':       #all connected clients
                response = []
                for i in all_data:
                    response.append(json.loads(i))
                response = json.dumps(response)
            else:   #returns list and data is mac address
                list_of_mac = json.loads(data)
                response = []
                for m_data in list_of_mac:
                    if m_data in mac_list:
                        for i in range(len(ip_address[m_data])):
                            local_response = dict()
                            local_response['ip'] = ip_address[m_data][i]
                            local_response['port'] = port_number[m_data][i]
                            local_response['mac'] = m_data
                            response.append(local_response)
                response = json.dumps(response)
            connection.sendall(str.encode(response))

    except ConnectionResetError:
        n = len(ip_address[mac_data])
        if(n==1):
            mac_list.remove(mac_data)
            ip_address.pop(mac_data)
            port_number.pop(mac_data)
        else:
            ip_address[mac_data].remove(ip_data)
            port_number[mac_data].remove(port_data)
        all_data.remove(uni_data_)
        connection.close()
        print('Connection closed: '+ip_data + ':' + str(port_data))

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' +address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, address,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSideSocket.close()
