from services.network_services.peerTLSInterface import PeerTLSInterface
import concurrent.futures

if __name__ == '__main__':
    buffers = dict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(7):
            ob = PeerTLSInterface(threadPoolExecutor = executor, remoteAddress = '192.168.0.103', localPort= 11111+i)
            fut = executor.submit(ob.connectToRemoteClient, networkPassword='P@ssw0rd', localRedundancyCount=2)
            buffers[fut] = i


    for fut in concurrent.futures.as_completed(buffers):
        print(buffers[fut], 'completer')
