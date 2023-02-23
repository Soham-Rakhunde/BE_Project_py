import base64
import json
from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.hmac_module import HMAC_Module
from services.network_services.hostTLSInterface import HostTLSInterface
import concurrent.futures
from collections import deque
from services.partitioning_module import Partitioner
from utils.constants import CHUNK_SIZE


class RetrieverModule:
    def __init__(self, tracker_path):
        self.tracker_path = tracker_path

    def retrieve(self):
        self.portadd = 0
        try:
            with open(self.tracker_path, 'r') as openfile:
                self.trackerJSON = json.load(openfile)
        except Exception as e:
            print(e)
            return
        print("Retriever: Decoded Tracker JSON from", self.tracker_path)

        mac_list = []
        for chunk in self.trackerJSON['chunks']:
            for peer in chunk['peers']:
                mac_list.append(peer['mac'])
        
        
        # update the entries with current IP addresses
        discovery = DiscoveryServiceInterface()
        discovery.retreive_known_peers(mac_addr_list=mac_list)


        for chunk in self.trackerJSON['chunks']:
            for peer in chunk['peers']:
                activePeer = next(iterator=filter(lambda activePeer: peer['mac-addr'] == activePeer['mac'], discovery.peersList), default=None)
                if activePeer == None:
                    print(f"Retriever: For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found inactive")
                else:
                    print(f"Retriever: For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found active at IP: {activePeer['ip']}")
                    peer['address'] = activePeer['ip']


        # Create the queue of iterators for each chunk
        self.chunkQueue = deque()
        self.chunkTryIndex = {}
        # here key is the chunk id and value is the index of the peer of that chunk['peers]list

        for chunk in self.trackerJSON['chunks']:
            self.chunkQueue.append(chunk['peers'][0] | {'id': chunk['id'], 'hmac': chunk['hmac']}) # add the chunk id for easier reference
            self.chunkTryIndex[chunk['id']] = 0

        self.buffers = dict()
        while len(self.chunkQueue) > 0:
            print("OUTER QUEUE SIZE", len(self.chunkQueue))
            self.receiveScheduler()
       
        mergedBuffer = Partitioner.merge(self.buffers)
        _dataHandler = DataHandler()
        _dataHandler.decode(buffer=mergedBuffer)
        
        EncryptionService.decrypt(_dataHandler)
        _dataHandler.write_file( save_path = f'C:\\Users\\soham\\OneDrive\\Desktop\\{self.trackerJSON["name"]}')

    def receiveScheduler(self):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(self.chunkQueue) > 0:
                print("INNER QUEUE SIZE", len(self.chunkQueue))
                curChunk = self.chunkQueue.popleft()
                print(curChunk, "curChunk")
                print("Retriever: Retrieving chunk", curChunk['id'])
                receiver = HostTLSInterface(
                    threadPoolExecutor = executor, 
                    remoteAddress = curChunk['address'], 
                    remotePort= 11111+self.portadd,
                    # remotePort= 11111+curChunk['id'],
                    retrievalMode= True,
                    locationsList=curChunk['locations'],
                    hmac=curChunk['hmac']
                ) #port change TODO
                self.portadd +=1
                fut = executor.submit(receiver.connectToRemoteServer, remotepassword ='P@ssw0rd')
                
                if fut != None:
                    self.buffers[fut] = curChunk['id']
                else:
                    # enque next peer with the same chunk
                    # if curChunk['id'] in self.chunkTryIndex:
                    self.chunkTryIndex[curChunk['id']] += 1
                    # else:
                    #     self.chunkTryIndex[curChunk['id']] = 1

                    chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunk['id'], self.trackerJSON['chunks']))
                    if(self.chunkTryIndex[curChunk['id']] >= len(chunkTrackerEntry['peers'])):
                        print("Retriever: No active peers for chunk", curChunk['id'])
                        return
                    nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunk['id']]]
                    print("Retriever: Peer not connected, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])
                    self.chunkQueue.append(nexChunk | {'id': chunkTrackerEntry['id'], 'hmac': chunkTrackerEntry['hmac']}) # add the chunk id for easier reference

        for fut in concurrent.futures.as_completed(self.buffers):
            # If data isnt found at peer
            curChunkId = self.buffers[fut]
            print(curChunkId, "Donee")
            if fut.result().getbuffer().nbytes != CHUNK_SIZE:
                self.chunkTryIndex[curChunkId] += 1
                chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunkId, self.trackerJSON['chunks']))
                if(self.chunkTryIndex[curChunkId] >= len(chunkTrackerEntry['peers'])):
                    print("Retriever: No active peers for chunk", curChunkId)
                    return
                nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunkId]]
                self.chunkQueue.append(nexChunk | {'id': chunkTrackerEntry['id'], 'hmac': chunkTrackerEntry['hmac']}) # add the chunk id for easier reference   
                print("Retriever: Data not found at Peer, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])

                self.buffers.pop(fut)
            else:
                curChunkId = self.buffers[fut]
                print("Retriever: Successfully retrieved chunk", curChunkId)
                # already handled inside hosttls interface
                # chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunkId, self.trackerJSON['chunks']))
                # chunk_data = fut.result().getvalue()
                # valid = HMAC_Module.verifyHMAC(
                #     msg=chunk_data,
                #     hmac=chunkTrackerEntry['hmac']
                # )
                # if valid:
                #     print("HMAC Checker: Succesfully verified the chunk for integrity and authenticity for chunk", curChunkId)
                # else:
                #     print("HMAC Checker: The data is corrupted or wrong key provided for chunk", curChunkId)
                #     self.chunkTryIndex[curChunkId] += 1
                #     if(self.chunkTryIndex[curChunkId] >= len(chunkTrackerEntry['peers'])):
                #         print("Retriever: No active peers for chunk", curChunkId)
                #         return
                #     nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunkId]]
                #     self.chunkQueue.append(nexChunk | {'id': chunkTrackerEntry['id'], 'hmac': chunkTrackerEntry['hmac']}) # add the chunk id for easier reference   
                #     print("Retriever: Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])
                #     self.buffers.pop(fut)

           
            # print(self.buffers[fut], fut.result().getbuffer().nbytes, fut.result(), type(fut.result().getbuffer()))
