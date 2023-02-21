from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.network_services.peerTLSInterface import PeerTLSInterface
import concurrent.futures
from services.network_services.peerTLSInterface import PeerTLSInterface
from services.partitioning_module import Partitioner

if __name__ == '__main__':
    buffers = dict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(7):
            print("START", i)
            ob = PeerTLSInterface(threadPoolExecutor = executor, remoteAddress = '192.168.0.103', localPort= 11111+i)
            fut = executor.submit(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            
            # fut = ob.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            # fut = ob.payloadFuture
            buffers[fut] = i
            print("LOOP", i)


    for fut in concurrent.futures.as_completed(buffers):
        # pass
        print(buffers[fut], 'completer')
        # print(buffers[fut], fut.result().getbuffer().nbytes, fut.result(), type(fut.result().getbuffer()))
    
    # if not in retrieval mode    
    # if not isinstance(list(buffers.keys())[0].result(), bytes):
    #     mergedBuffer = Partitioner.merge(buffers)   
    #     _dataHandler = DataHandler()
    #     _dataHandler.decode(buffer=mergedBuffer)
        
    #     EncryptionService.decrypt(_dataHandler)
    #     _dataHandler.write_file()
