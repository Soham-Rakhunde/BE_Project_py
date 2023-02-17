import socket
import urllib.request
import re, uuid

ClientMultiSocket = socket.socket()
ClientMultiSocket.bind(('0.0.0.0', 0))
ClientMultiSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

localPort = ClientMultiSocket.getsockname()[1]

mac_add =  (':'.join(re.findall('..', '%012x' % uuid.getnode())))

external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')

host = '127.0.0.1'
port = 2004
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(1024)

ClientMultiSocket.send(str.encode(str(mac_add)+' '+str(external_ip)+' '+str(localPort)))


while True:
    Input = input('Enter: ')
    ClientMultiSocket.send(str.encode(Input))
    res = ClientMultiSocket.recv(1024)
    print(res.decode('utf-8'))
        
ClientMultiSocket.close()
