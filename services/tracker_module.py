import base64
import io, json
from services.hmac_module import HMAC_Module
# from services.network_services.p2p_network_handler import P2PNetworkHandler
from utils.constants import *
import pprint
import concurrent.futures

from services.network_services.senderTLSInterface import TLSender

class Tracker:
    bufferObj: io.BufferedIOBase = None

    def __init__(self, bufferObj: io.BufferedIOBase) -> None:
        self.bufferObj = bufferObj

    def send_chunks(self, _dataHandler):
        self.bufferObj.seek(0)
        num_of_chunks = self.bufferObj.getbuffer().nbytes
        print("Chunks in nums ",int(num_of_chunks / CHUNK_SIZE))

        futuresDict = dict()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(int(num_of_chunks / CHUNK_SIZE)):
                print("CHUNK", i)
                chunk = self.bufferObj.read(CHUNK_SIZE)
                hmac = HMAC_Module.generateHMAC(chunk) # TODO: save HMAC in traceker file
                ob = TLSender(payload= chunk, threadPoolExecutor = executor, remoteAddress = '192.168.179.75', remotePort =11111+i)
                
                # res = executor.map(ob.connectToRemoteServer, remotepassword='P@ssw0rd')
                ob.connectToRemoteServer(remotepassword='P@ssw0rd')
                future = ob.remoteLocationFuture
                futuresDict[future] = {
                    'id': i,
                    'hmac':  base64.b64encode(hmac).decode("ascii")
                }
                # futs.append(ob.connectToRemoteServer(remotepassword='P@ssw0rd'))
                print("LOOP", i)
                
            trackerJSON = dict()
            trackerJSON['name'] = "FileName.jpeg" #TODO: add original names and data for tracekr 
            trackerJSON['chunk_count'] = num_of_chunks
            trackerJSON['chunks'] = []

            for fut in concurrent.futures.as_completed(futuresDict): 
                print(fut.result())
                trackerJSON['chunks'].append({
                    'id': futuresDict[fut]['id'],
                    'hmac': futuresDict[fut]['hmac'],
                    'peers': [{
                        'address': '192.168.179.75',
                        'mac-addr': '00:00:00:00:00:00',
                        'locations': [fut.result()]
                    }]
                })


            with open('Identity/tracker.json', 'w') as file:
                json.dump(trackerJSON, file)