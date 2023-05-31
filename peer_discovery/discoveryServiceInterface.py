import socket
import urllib.request
import re, uuid
import json
from subprocess import check_output
import platform
import gradio as gr
from ui.printer import Printer
from utils.singleton_meta import SingletonMeta

# class SingletonMeta(type):
#     """
#     The Singleton class can be implemented in different ways in Python. Some
#     possible methods include: base class, decorator, metaclass. We will use the
#     metaclass because it is best suited for this purpose.
#     """

#     _instances = {}

#     def __call__(cls, *args, **kwargs):
#         """
#         Possible changes to the value of the `__init__` argument do not affect
#         the returned instance.
#         """
#         if cls not in cls._instances:
#             instance = super().__call__(*args, **kwargs)
#             cls._instances[cls] = instance
#         return cls._instances[cls]

class DiscoveryServiceInterface(metaclass=SingletonMeta):
    server_ip = '192.168.96.50'
    server_port = 11100
    mac_add =  (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    try:
        external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
    except:
        raise gr.Error("Not connected to any network")
    
    # print(socket.gethostbyname_ex(hostname))
    # IPAddr = socket.gethostbyname_ex(hostname)[2][0]
    
    if platform.uname().system == 'Windows':
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname_ex(hostname)[-1][-1]
    else: 
        IPAddr = str(check_output(['hostname', '--all-ip-addresses'])).split(' ')[0][2:]
    print(IPAddr)

    

    def __init__(self):
        self.clientMultiSocket = socket.socket()
        self.clientMultiSocket.bind(('0.0.0.0', 0))
        self.clientMultiSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        localPort = self.clientMultiSocket.getsockname()[1] 
        self.printer = Printer()
        self.printer.write(name='Discovery', msg=f"Bound to local port: {localPort}")

        print('Discovery: Waiting for connection response')
        self.printer.write(name='Discovery', msg=f"Sending connection request to Discovery Server at {self.server_port}:{self.server_port}")
        try:
            self.clientMultiSocket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(str(e))
            return
        res = self.clientMultiSocket.recv(1024)

        d_data = {'ip': self.IPAddr , 'port':localPort, 'mac':self.mac_add}
        self.printer.write(name='Discovery', msg=f"Sending location info to Discovery Server: {d_data}")
        data = json.dumps(d_data)
        self.clientMultiSocket.sendall(bytes(data,encoding="utf-8"))
        
    def retrieve_peers(self):
        self.clientMultiSocket.sendall(str.encode('1'))
        res = self.clientMultiSocket.recv(1024)
        self.peersList = json.loads(res)

        # self.peersList.remove('192.168.96.50')
        for i in range(len(self.peersList)):
            if self.peersList[i]['ip'] == self.IPAddr:
                del self.peersList[i]
                break

        print("Discovery: available peers: ", self.peersList)
        self.printer.write(name='Discovery', msg=f"Retrieving peers: {self.peersList}")

    def retreive_known_peers(self, mac_addr_list: list):
        json_data = json.dumps(mac_addr_list)
        self.clientMultiSocket.sendall(str.encode(json_data))
        res = self.clientMultiSocket.recv(1024)
        self.peersList = json.loads(res)
        
        for i in range(len(self.peersList)):
            if self.peersList[i]['ip'] == self.IPAddr:
                del self.peersList[i]
                break
        print("Discovery: available peers: ", self.peersList)
        self.printer.write(name='Discovery', msg=f"Retrieving known peers: {self.peersList}")
        

    def __del__(self):
        self.printer.write(name='Discovery', msg=f"Closing conneciton")
        self.clientMultiSocket.close()

if __name__ == "__main__":
    d = DiscoveryServiceInterface()

    d.retrieve_peers()
    d.retreive_known_peers([d.mac_add])