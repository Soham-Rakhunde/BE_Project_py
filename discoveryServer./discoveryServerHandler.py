import socket
import urllib.request
import re, uuid
import json

class DiscoveryServerInterface:
    server_ip, server_port = '127.0.0.1', 2004
    mac_address = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')

    def __init__(self):
        self.clientMultiSocket = socket.socket()
        self.clientMultiSocket.bind(('0.0.0.0', 0))
        self.clientMultiSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.localPort = self.clientMultiSocket.getsockname()[1]

        print('Discovery: Waiting for connection response')
        try:
            self.clientMultiSocket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
        res = self.clientMultiSocket.recv(1024)
        print(res.decode('utf-8'))

        d_data = {'ip': self.external_ip, 'port':self.localPort, 'mac':self.mac_address}
        data = json.dumps(d_data)
        self.clientMultiSocket.sendall(bytes(data,encoding="utf-8"))
        print("Discovery: Discovery Server Connected")

    def retrieve_peers(self):
        self.clientMultiSocket.send(str.encode('1'))
        res = self.clientMultiSocket.recv(1024)
        res = res.decode('utf-8')
        res = json.loads(res)
        self.peersList = res
        return res

    def retreive_known_peers(self):
        d_data = [self.mac_address]
        data = json.dumps(d_data)
        self.clientMultiSocket.sendall(str.encode(data))
        res = self.clientMultiSocket.recv(1024)
        res = res.decode('utf-8')
        res = json.loads(res)
        self.peersList = res
        return res

    def __del__(self):
        self.clientMultiSocket.close()

a = DiscoveryServerInterface()
while(True):
    i = input("Enter: ")
    res = ''
    if(i=='1'):
        res = a.retrieve_peers()
    elif(i=='2'):
        res = a.retreive_known_peers()
    else:
        del a
        break
    print(res)
