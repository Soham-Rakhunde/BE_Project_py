import base64
import io, json
import pprint
import concurrent.futures

from utils.constants import *
from services.hmac_module import HMAC_Module
from services.network_services.hostTLSInterface import HostTLSInterface

class Tracker:
    bufferObj: io.BufferedIOBase = None

    def __init__(self, bufferObj: io.BufferedIOBase) -> None:
        self.bufferObj = bufferObj

    peersList = [
        {'ip': '192.168.0.103', 'port':11111, 'mac':'44:AF:28:F2:EB:3A'},
        {'ip': '192.168.0.103', 'port':11112, 'mac':'44:AF:28:F2:EB:3A'},
        {'ip': '192.168.0.103', 'port':11113, 'mac':'44:AF:28:F2:EB:3A'},
        {'ip': '192.168.0.103', 'port':11114, 'mac':'44:AF:28:F2:EB:3A'},
        {'ip': '192.168.0.103', 'port':11115, 'mac':'44:AF:28:F2:EB:3A'},
        {'ip': '192.168.0.103', 'port':11116, 'mac':'44:AF:28:F2:EB:3A'}
    ]


    def is_compatible_reduncancy_ratio(self):
        if len(self.peerList) < (self.nodes_redundancy_ratio*self.num_of_chunks):
            print("Excecption: Too high redundancy ratio")
            return False
        return True

    def send_chunks(self, _dataHandler):
        self.bufferObj.seek(0)
        self.totalSize = self.bufferObj.getbuffer().nbytes
        self.num_of_chunks = int(self.totalSize / CHUNK_SIZE)

        # TODO: Input redundancy ratio
        self.nodes_redundancy_ratio = 1
        self.nodewise_redundancy_ratio = 1
        
        print("Chunks in nums ",self.num_of_chunks)

        # while self.is_compatible_reduncancy_ratio():
        # TODO input new redundancy ratio

        futuresDict = dict()
        with concurrent.futures.ThreadPoolExecutor() as executor:

            # iterate each chunk
            for chunk_id in range(self.num_of_chunks):
                print("CHUNK", chunk_id)
                chunk = self.bufferObj.read(CHUNK_SIZE)
                hmac = HMAC_Module.generateHMAC(chunk) # TODO: save HMAC in traceker file

                #iterate for redundancy over multiple peers
                for peer_number in range(chunk_id*self.nodes_redundancy_ratio, 
                               self.nodes_redundancy_ratio*(chunk_id+1)):
                    # peer_number = int(self.num_of_chunks / CHUNK_SIZE)*(chunk_id) +j
                    # print("ZZ, ",chunk_id, j, peer_number)
                    print("Tracker: Initaiting with peernumber", peer_number)
                    sendHandler = HostTLSInterface(
                        payload= chunk, 
                        threadPoolExecutor = executor, 
                        remoteAddress = self.peersList[peer_number]['ip'], 
                        # remotePort = self.peersList[peer_number]['ip'] TODO
                        remotePort = 11111 + peer_number
                    )
                    future = executor.submit(sendHandler.connectToRemoteServer, remotepassword ='P@ssw0rd')
                
                    # sendHandler.connectToRemoteServer(remotepassword='P@ssw0rd')
                    # future = sendHandler.locationFuture
                    print("BLOJ ", peer_number)
                    futuresDict[future] = {
                        'id': chunk_id,
                        'hmac':  base64.b64encode(hmac).decode("ascii"),
                        'address': self.peersList[peer_number]['ip'],
                        'mac_addr': self.peersList[peer_number]['mac']
                    }
                    print("LOJ ", peer_number)
                print("LOOP ", chunk_id)
            
            self.trackerFileCreator(futuresDict)
            

    def trackerFileCreator(self, futuresDict:dict):
        trackerJSON = dict()
        trackerJSON['name'] = "FileName.jpeg" #TODO: add original names and data for tracekr 
        trackerJSON['chunk_count'] = self.num_of_chunks
        trackerJSON['chunks'] = []

        # print(next(filter(lambda chunk: chunk['id'] == futuresDict[fut]['id'], trackerJSON['chunks'])))


        for fut in concurrent.futures.as_completed(futuresDict): 
            print(fut.result())

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


        with open('Identity/tracker.json', 'w') as file:
            json.dump(trackerJSON, file)