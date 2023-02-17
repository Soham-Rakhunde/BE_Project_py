import json
from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.network_services.remoteTLSInterface import HostTLS
import concurrent.futures
from collections import deque
from services.partitioning_module import Partitioner
from utils.constants import CHUNK_SIZE

class Retriever:
    def __init__(self, tracker_path):
        self.tracker_path = tracker_path

    def retrieve(self):
        try:
            with open(self.tracker_path, 'r') as openfile:
                self.trackerJSON = json.load(openfile)
        except Exception as e:
            print(e)
            return
        print("Retriever: Decoded Tracker JSON from", self.tracker_path)

        # Create the queue of iterators for each chunk
        self.chunkQueue = deque()
        for chunk in self.trackerJSON['chunks']:
            self.chunkQueue.append(chunk['peers'][0])

        self.buffers = dict()
        self.chunkTryIndex = {} # 0th index is not appended only from the next try
        # here key is the chunk id and value is the index of the peer of that chunk['peers]list

        while len(self.chunkQueue) > 0:
            print("OUTER QUEUE SIZE", len(self.chunkQueue))
            self.receiveScheduler()
       
        mergedBuffer = Partitioner.merge(self.buffers)
        _dataHandler = DataHandler()
        _dataHandler.decode(buffer=mergedBuffer)
        
        EncryptionService.decrypt(_dataHandler)
        _dataHandler.write_file()

    def receiveScheduler(self):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(self.chunkQueue) > 0:
                print("INNER QUEUE SIZE", len(self.chunkQueue))
                curChunk = self.chunkQueue.popleft()
                
                print("Retriever: Retrieving chunk", curChunk['id'])
                receiver = HostTLS(threadPoolExecutor = executor, remoteAddress = curChunk['address'], localPort= 11111+curChunk['id']) #port change TODO
                fut = executor.submit(receiver.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
                
                if fut != None:
                    self.buffers[fut] = curChunk['id']
                else:
                    # enque next peer with the same chunk
                    if curChunk['id'] in self.chunkTryIndex:
                        self.chunkTryIndex[curChunk['id']] += 1
                    else:
                        self.chunkTryIndex[curChunk['id']] = 1

                    chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunk['id'], self.trackerJSON['chunks']))
                    if(self.chunkTryIndex[curChunk['id']] >= len(chunkTrackerEntry['peers'])):
                        print("Retriever: No active peers for chunk", curChunk['id'])
                        return
                    nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunk['id']]]
                    print("Retriever: Peer not connected, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])
                    self.chunkQueue.append(nexChunk)

        for fut in concurrent.futures.as_completed(self.buffers):
            # If data isnt found at peer
            curChunkId = self.buffers[fut]
            if fut.result().getbuffer().nbytes != CHUNK_SIZE:
                chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunkId, self.trackerJSON['chunks']))
                if(self.chunkTryIndex[curChunkId] >= len(chunkTrackerEntry['peers'])):
                    print("Retriever: No active peers for chunk", curChunkId)
                    return
                nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunkId]]
                self.chunkQueue.append(nexChunk)    
                print("Retriever: Data not found at Peer, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])

                self.buffers.pop(fut)
            else:
                print("Retriever: Successfully retrieved chunk", curChunkId)
            # print(self.buffers[fut], fut.result().getbuffer().nbytes, fut.result(), type(fut.result().getbuffer()))
