import concurrent.futures
from services.network_services.senderTLSInterface import TLSender

def sender(tlsSender):
    print("C: sending payload")
    tlsSender.clientSocket.send(bytes(tlsSender.payload,'utf-8'))
    # self.peerMAC = self.recieveSocket.recv() TODO: receive the loacation
    tlsSender.clientSocket.close()
    print("Closing sockets")

if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor() as multiProcessExecutor:
        print('create')
        ob = TLSender(payload= "HIII", multiProcessExecutor = multiProcessExecutor, remoteAddress = '192.168.0.105', remotePort =11111)
        print('dsdse')
        ob.connectToRemoteServer(remotepassword='P@ssw0rd')
        print('yyy')
        # res = multiProcessExecutor.submit(sender, ob)
        # print('zzzaswq')
        # print(res.result())

