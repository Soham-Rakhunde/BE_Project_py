import socket
import urllib.request
import re, uuid

from utils.singleton_meta import SingletonMeta


class DiscoveryServerInterface(metaclass=SingletonMeta):
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

        self.clientMultiSocket.send(str.encode(str(self.mac_address)+' '+str(self.external_ip)+' '+str(self.localPort)))
        print("Discovery: Discovery Server Connected")

    def retrieve_peers(self):
        # TODO: uncomment this and change the decoding to JSON instead
        self.clientMultiSocket.send(str.encode(1))
        res = self.clientMultiSocket.recv(1024)
        print(res.decode('utf-8'))
        self.peersList = [
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'},
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'},
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'}
        ]
        # while True:
        #     Input = input('Enter: ')
        #     self.clientMultiSocket.send(str.encode(Input))
        #     res = self.clientMultiSocket.recv(1024)
        #     print(res.decode('utf-8'))

    def retreive_known_peers(self):
        self.clientMultiSocket.send(str.encode('44:AF:28:F2:EB:3A'))
        res = self.clientMultiSocket.recv(1024)
        print(res.decode('utf-8'))
        self.peersList = [
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'},
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'},
            {'ip': '192.168.0.103', 'port':'', 'mac':'44:AF:28:F2:EB:3A'}
        ]

    def __del__(self):
        self.clientMultiSocket.close()