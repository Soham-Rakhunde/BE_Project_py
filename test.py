import json
from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.network_services.peerTLSInterface import PeerTLSInterface
import concurrent.futures
from collections import deque
from services.network_services.peerTLSInterface import PeerTLSInterface
from services.partitioning_module import Partitioner
from utils.constants import CHUNK_SIZE

if __name__ == '__main__':
    
    buffers = dict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(3):
            print("START", i)
            ob = PeerTLSInterface(threadPoolExecutor = executor, remoteAddress = '192.168.0.103', localPort= 11111+i)
            fut = executor.submit(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            
            # fut = ob.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            # fut = ob.payloadFuture
            buffers[fut] = i
            print("LOOP", i)


    for fut in concurrent.futures.as_completed(buffers):
        # pass
        print(buffers[fut], fut.result().getbuffer().nbytes, fut.result(), type(fut.result().getbuffer()))

    mergedBuffer = Partitioner.merge(buffers)
    _dataHandler = DataHandler()
    _dataHandler.decode(buffer=mergedBuffer)
    
    EncryptionService.decrypt(_dataHandler)
    _dataHandler.write_file()
