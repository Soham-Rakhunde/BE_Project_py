from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.network_services.receiverTLSInterface import TLSReceiver
import concurrent.futures

from services.partitioning_module import Partitioner

if __name__ == '__main__':
    
    buffers = dict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(3):
            print("START", i)
            ob = TLSReceiver(threadPoolExecutor = executor, remoteAddress = '192.168.9.75', localPort= 11111+i)
            # res = executor.map(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            fut = executor.submit(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            buffers[fut] = i
            print("LOOP", i)


    for fut in concurrent.futures.as_completed(buffers):
        pass
        # print(buffers[fut], fut.result().getbuffer().nbytes, fut.result(), type(fut.result().getbuffer()))

    mergedBuffer = Partitioner.merge(buffers)
    _dataHandler = DataHandler()
    _dataHandler.decode(buffer=mergedBuffer)
    
    EncryptionService.decrypt(_dataHandler)
    _dataHandler.write_file()