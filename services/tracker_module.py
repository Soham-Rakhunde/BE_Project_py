import io, json
import concurrent.futures
import os
from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from ui.dataAccumlator import DataLogger
from ui.printer import Printer

from utils.constants import *
from services.hmac_module import HMAC_Module
from services.network_services.hostTLSInterface import HostTLSInterface
import gradio as gr

class Tracker:
    bufferObj: io.BufferedIOBase = None
    progress = None

    # UI functions

    def progress_update(self, percent, desc):
        if self.progress != None:
            self.progress(percent/100, desc=desc, unit="percent")

    def progress_tqdm(self, iter, desc, unit, total=None):
        if self.progress != None:
            return self.progress.tqdm(iter, desc=desc, unit=unit, total=total)
        else:
            return iter


    def __init__(
        self,
        bufferObj: io.BufferedIOBase, 
        redundancyRatio = 2, 
        fileName:str ="FileName.jpeg",
        progress: gr.Progress = None
    ) -> None:
        self.bufferObj = bufferObj
        discovery = DiscoveryServiceInterface()
        discovery.retrieve_peers()
        self.printer = Printer()
        self.peersList = discovery.peersList
        self.progress = progress
        self.nodes_redundancy_ratio = redundancyRatio
        self.fileName = fileName

    def is_compatible_reduncancy_ratio(self):
        if len(self.peersList) < (self.nodes_redundancy_ratio*self.num_of_chunks):
            print("Excecption: Too high redundancy ratio")
            self.printer.write(
                name='Tracker', msg='Excecption: Too high redundancy ratio')
            return False
        return True

    def send_chunks(self, network_passwd):
        self.bufferObj.seek(0)
        self.totalSize = self.bufferObj.getbuffer().nbytes
        self.num_of_chunks = int(self.totalSize / CHUNK_SIZE)
        hostLogs = DataLogger()
        hostLogs.commonInfoList[0][2] = self.num_of_chunks
        hostLogs.commonInfoList[0][4] = self.nodes_redundancy_ratio
        hostLogs.commonInfoList[0][5] = self.nodes_redundancy_ratio*self.num_of_chunks

        # TODO: Input redundancy ratio
        self.nodewise_redundancy_ratio = 2
        
        print("Chunks in nums ",self.num_of_chunks)
        self.printer.write(
            name='Tracker', msg='Excecption: Too high redundancy ratio')

        if not self.is_compatible_reduncancy_ratio():
            return

        futuresDict = dict()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # iterate each chunk
            chunk_id = 0
            for chunk_id in self.progress_tqdm(iter=range(self.num_of_chunks), 
                                               desc=f'Scheduling Chunk {chunk_id} to be sent to {self.nodes_redundancy_ratio} peers each',
                                               unit="Chunk"):
                print("CHUNK", chunk_id)
                self.printer.write(
                    name=f'Chunk-{chunk_id}:Tracker', msg=f'Preparing Chunk {chunk_id} to be sent to peers')
                
                chunk = self.bufferObj.read(CHUNK_SIZE)
                hmac = HMAC_Module.generateHMAC(chunk) # TODO: save HMAC in traceker file
                self.printer.write(
                    name=f'Chunk-{chunk_id}:HMAC service', msg=f'Generated HMAC for chunk {chunk_id} with 128 bit key')
                #iterate for redundancy over multiple peers

                peer_number = chunk_id*self.nodes_redundancy_ratio
                for peer_number in self.progress_tqdm(iter=range(chunk_id*self.nodes_redundancy_ratio, self.nodes_redundancy_ratio*(chunk_id+1)), 
                                                      desc=f'Scheduling Chunk-{chunk_id} to Peer-{peer_number}',
                                                      unit="Peer"):
                    # peer_number = int(self.num_of_chunks / CHUNK_SIZE)*(chunk_id) +j
                    # print("ZZ, ",chunk_id, j, peer_number)
                    print("Tracker: Initaiting with peernumber", peer_number)
                    sendHandler = HostTLSInterface(
                        payload= chunk, 
                        threadPoolExecutor = executor, 
                        remoteAddress = self.peersList[peer_number]['ip'], 
                        # remotePort = self.peersList[peer_number]['ip'] TODO
                        # remotePort = 11111 + peer_number,
                        remotePort = 11111,
                        chunkId=chunk_id,
                        peerId=peer_number
                    )
                    self.printer.write(
                        name=f'Chunk-{chunk_id}:Peer-{peer_number}:Tracker', msg=f'Generated HMAC for chunk {chunk_id} with 128 bit key')
                    future = executor.submit(sendHandler.connectToRemoteServer, networkPassword =network_passwd)
                
                    # sendHandler.connectToRemoteServer(remotepassword='P@ssw0rd')
                    # future = sendHandler.locationFuture
                    futuresDict[future] = {
                        'id': chunk_id,
                        'hmac':  hmac, 
                        'address': self.peersList[peer_number]['ip'],
                        'mac_addr': self.peersList[peer_number]['mac']
                    }
            
            self.printer.write(name="Tracker", msg=f"Generating and saving tracker JSON file as {self.fileName.split('.')[0]}.json")
            trackerJson =self.trackerFileCreator(futuresDict)
            self.printer.write(name="Tracker", msg="Succesfuly completed.")
            return trackerJson
            

    def trackerFileCreator(self, futuresDict:dict):
        trackerJSON = dict()
        trackerJSON['name'] = self.fileName #TODO: add original names and data for tracekr 
        trackerJSON['chunk_count'] = self.num_of_chunks
        trackerJSON['chunks'] = []

        # print(next(filter(lambda chunk: chunk['id'] == futuresDict[fut]['id'], trackerJSON['chunks'])))

        
        for fut in self.progress_tqdm(
            iter=concurrent.futures.as_completed(futuresDict), 
            desc="Waiting for all threads to finish", 
            unit='Threads', 
            total=len(futuresDict)
        ): 
            hostLogs = DataLogger()
            hostLogs.commonInfoList[0][3] += 1
            # print(fut.result())
            try: # if id present then update inital entry
                chunkTrackerEntry = next(filter(lambda chunk: chunk['id'] == futuresDict[fut]['id'], trackerJSON['chunks']))
                chunkTrackerEntry['peers'].append({
                    'address': futuresDict[fut]['address'],
                    'mac-addr': futuresDict[fut]['mac_addr'],
                    'locations': fut.result()
                })
            except: #else create new entry
                trackerJSON['chunks'].append({
                    'id': futuresDict[fut]['id'],
                    'hmac': futuresDict[fut]['hmac'],
                    'peers': [{
                        'address': futuresDict[fut]['address'],
                        'mac-addr': futuresDict[fut]['mac_addr'],
                        'locations': fut.result()
                    }]
            })


        self.progress_update(percent=95, desc="Sent and received acknowledgements for all chunks from all peers")
        if not os.path.isdir('Temp'):
            os.mkdir('Temp')
        with open(f'Temp/tracker_{self.fileName}.json', 'w') as file:
            json.dump(trackerJSON, file)
        return trackerJSON