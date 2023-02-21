import socket
import urllib.request
import re, uuid
import json,sys

from utils.singleton_meta import SingletonMeta

class DiscoveryServiceInterface(metaclass=SingletonMeta):
    server_ip = '127.0.0.1'
    server_port = 11100
    mac_add =  (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
    

    def __init__(self):
        self.clientMultiSocket = socket.socket()
        self.clientMultiSocket.bind(('0.0.0.0', 0))
        self.clientMultiSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        localPort = self.clientMultiSocket.getsockname()[1]

        print('Discovery: Waiting for connection response')
        try:
            self.clientMultiSocket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            return
        res = self.clientMultiSocket.recv(1024)

        d_data = {'ip': self.external_ip, 'port':localPort, 'mac':self.mac_add}
        data = json.dumps(d_data)
        self.clientMultiSocket.sendall(bytes(data,encoding="utf-8"))
        
    def retrieve_peers(self):
        # TODO: uncomment this and change the decoding to JSON instead
        self.clientMultiSocket.sendall(str.encode(1))
        res = self.clientMultiSocket.recv(1024)
        self.peersList = json.loads(res)
        print("Discovery: available peers: ", self.peersList)

    def retreive_known_peers(self, mac_addr_list: list):
        json_data = json.dumps(mac_addr_list)
        self.clientMultiSocket.sendall(str.encode(json_data))
        res = self.clientMultiSocket.recv(1024)
        self.peersList = json.loads(res)
        print("Discovery: available peers: ", self.peersList)
        

    def __del__(self):
        self.clientMultiSocket.close()