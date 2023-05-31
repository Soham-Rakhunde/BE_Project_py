import json
import os
import platform
from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.network_services.hostTLSInterface import HostTLSInterface
import concurrent.futures
from collections import deque
from services.partitioning_module import Partitioner
from ui.dataAccumlator import DataLogger
from ui.printer import Printer
from utils.constants import CHUNK_SIZE
import gradio as gr

class RetrieverModule:
    def __init__(self, tracker_path, network_passwd, progress: gr.Progress = None):
        self.tracker_path = tracker_path
        self.progress = progress
        self.printer = Printer()
        self.network_passwd = network_passwd

    # UI functions
    def progress_update(self, percent, desc):
        if self.progress != None:
            self.progress(percent/100, desc=desc, unit="percent")

    def progress_tqdm(self, iter, desc, unit, total=None):
        if self.progress != None:
            return self.progress.tqdm(iter, desc=desc, unit=unit, total=total)
        else:
            return iter


    def retrieve(self):
        self.portadd = 0
        try:
            with open(self.tracker_path, 'r') as openfile:
                self.trackerJSON = json.load(openfile)
        except Exception as e:
            print(e)
            return
        print("Retriever: Decoded Tracker JSON from", self.tracker_path)
        self.printer.write(
                name='Retriever', msg='Decoded Tracker JSON from ${self.tracker_path}')
        self.hostLogs = DataLogger()
        self.hostLogs.retrieverInfoList[0][1] = self.trackerJSON['chunk_count']

        mac_list = []
        for chunk in self.trackerJSON['chunks']:
            for peer in chunk['peers']:
                mac_list.append(peer['mac-addr'])
        


        self.printer.write(name='Retriever', msg='Gathering peer information where chunks is saved')
        self.progress_update(percent=1, desc='Gathering peer information where chunks is saved')
        
        # update the entries with current IP addresses
        discovery = DiscoveryServiceInterface()
        discovery.retreive_known_peers(mac_addr_list=mac_list)


        for chunk in self.trackerJSON['chunks']:
            for peer in self.progress_tqdm(iter=chunk['peers'], desc="Checking if Peers are active", unit="Peers"):
                activePeer = next(filter(lambda activePeer: peer['mac-addr'] == activePeer['mac'], discovery.peersList), None)
                if activePeer == None:
                    self.printer.write(name='Retriever', msg=f"For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found inactive")
                    print(f"Retriever: For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found inactive")
                    self.hostLogs.retrieverInfoList[0][6] += 1
                else:
                    self.printer.write(name='Retriever', msg=f"For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found active at IP: {activePeer['ip']}")
                    print(f"Retriever: For Chunk-{chunk['id']} peer with Mac address {peer['mac-addr']} found active at IP: {activePeer['ip']}")
                    peer['address'] = activePeer['ip']
                    self.hostLogs.retrieverInfoList[0][3] += 1

        self.hostLogs.retrieverInfoList[0][4] = self.hostLogs.retrieverInfoList[0][3] - self.trackerJSON['chunk_count']

        # Create the queue of iterators for each chunk
        self.chunkQueue = deque()
        self.chunkTryIndex = {}
                    
        # here key is the chunk id and value is the index of the peer of that chunk['peers]list

        self.printer.write(name='Retriever', msg=f"Intitalising network scheduler queue to retrieve each Chunk parallelly")
        self.progress_update(percent=10, desc='Intitalising network scheduler queue to retrieve each Chunk parallelly')
        for chunk in self.trackerJSON['chunks']:
            self.chunkQueue.append(chunk['peers'][0] | {'id': chunk['id'], 'hmac': chunk['hmac']}) # add the chunk id for easier reference
            self.chunkTryIndex[chunk['id']] = 0

        self.buffers = dict()
        while len(self.chunkQueue) > 0:
            print("OUTER QUEUE SIZE", len(self.chunkQueue))
            self.receiveScheduler()
       
        self.printer.write(name='Retriever', msg="All chunks received succesfully")
        self.progress_update(percent=80, desc="All chunks received succesfully")
        

        mergedBuffer = Partitioner.merge(self.buffers)
        self.printer.write(name='Retriever', msg="Ordering and merging all chunks into one buffer")
        self.progress_update(percent=85, desc="Merged all chunk in correct order into one buffer")

        
        if platform.uname().system == 'Windows':
            path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
        else: 
            path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 

        _dataHandler = DataHandler(file_path=path, filename="srwe.png")
        self.progress_update(percent=88, desc="Decoding the buffer...")
        _dataHandler.decode(buffer=mergedBuffer)
        
        self.progress_update(percent=92, desc="Decrypting the cipher...")
        EncryptionService.decrypt(_dataHandler)

        self.progress_update(percent=98, desc=f"Saving file as {path}\{self.trackerJSON['name']}")
        _dataHandler.write_file( save_path = f'{path}\{self.trackerJSON["name"]}')

        self.progress_update(percent=100, desc=f"Succesfully Retrieved file")
        return f'{path}\{self.trackerJSON["name"]}'

    def receiveScheduler(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(self.chunkQueue) > 0:
                curChunk = self.chunkQueue.popleft()
                self.printer.write(name=f"Retriever", msg=f"Retrieving Chunk {curChunk['id']} from Peer with IP: {curChunk['address']}")
                self.progress_update(percent=15, desc=f"Retrieving Chunk {curChunk['id']} from Peer with IP: {curChunk['address']}")
                print("Retriever: Retrieving chunk", curChunk['id'])
                receiver = HostTLSInterface(
                    threadPoolExecutor = executor, 
                    remoteAddress = curChunk['address'], 
                    remotePort= 11111,
                    # remotePort= 11111+self.portadd,
                    retrievalMode= True,
                    locationsList=curChunk['locations'],
                    hmac=curChunk['hmac']
                ) #port change TODO
                self.portadd +=1
                fut = executor.submit(receiver.connectToRemoteServer, networkPassword =self.network_passwd)
                
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
                        self.printer.write(name=f"Retriever(Error)", msg=f"No active peers for chunk{curChunk['id']}, Aborting...")
                        raise gr.Error(f"No active peers for chunk{curChunk['id']}")
                        return
                    nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunk['id']]]
                    print("Retriever: Peer not connected, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])
                    self.printer.write(name=f"Retriever", msg=f"Peer not connected, Rescheduling chunk {curChunk['id']}, try-{1+self.chunkTryIndex[curChunk['id']]}")
                    self.progress_update(percent=15, desc=f"Peer not connected, Rescheduling chunk {curChunk['id']}, try-{1+self.chunkTryIndex[curChunk['id']]}")
                    self.chunkQueue.append(nexChunk | {'id': chunkTrackerEntry['id'], 'hmac': chunkTrackerEntry['hmac']}) # add the chunk id for easier reference
                    self.hostLogs.retrieverInfoList[0][5] += 1

        for fut in self.progress_tqdm(
            iter=concurrent.futures.as_completed(self.buffers), 
            desc="Waiting for all threads to finish receiving correct data", 
            unit='Threads', 
            total=len(self.buffers)
        ):
            # If data isnt found at peer
            curChunkId = self.buffers[fut]
            if fut.result().getbuffer().nbytes != CHUNK_SIZE:
                self.chunkTryIndex[curChunkId] += 1
                chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == curChunkId, self.trackerJSON['chunks']))
                if(self.chunkTryIndex[curChunkId] >= len(chunkTrackerEntry['peers'])):
                    self.printer.write(name=f"Retriever(Error)", msg=f"No active peers for chunk{curChunk['id']}, Aborting...")
                    print("Retriever: No active peers for chunk", curChunkId)
                    raise gr.Error(f"No active peers for chunk{curChunk['id']}")
                    return
                nexChunk = chunkTrackerEntry['peers'][self.chunkTryIndex[curChunkId]]
                self.chunkQueue.append(nexChunk | {'id': chunkTrackerEntry['id'], 'hmac': chunkTrackerEntry['hmac']}) # add the chunk id for easier reference   
                print("Retriever: Data not found at Peer, Rescheduling chunk", curChunk['id'], ' try-',1+self.chunkTryIndex[curChunk['id']])
                self.printer.write(name=f"Retriever", msg=f"Data not found at Peer, Rescheduling chunk {curChunk['id']}, try-{1+self.chunkTryIndex[curChunk['id']]}")
                self.hostLogs.retrieverInfoList[0][5] += 1
                    
                self.buffers.pop(fut)
            else:
                curChunkId = self.buffers[fut]
                print("Retriever: Successfully retrieved chunk", curChunkId)
                self.hostLogs.retrieverInfoList[0][2] += 1
                self.printer.write(name=f"Retriever", msg=f"Successfully retrieved chunk {curChunkId}")
                  
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
