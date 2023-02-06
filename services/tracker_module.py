import io
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

    def send_chunks(self):
        # TODO call p2pnetworkhandler for each chunk
        print("send_chunks")
        self.bufferObj.seek(0)
        num_of_chunks = self.bufferObj.getbuffer().nbytes
        print("Chunks in nums ",int(num_of_chunks / CHUNK_SIZE))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(0, int(num_of_chunks / CHUNK_SIZE)):
                print("CHUNK", i)
                chunk = self.bufferObj.read(CHUNK_SIZE)
                hmac = HMAC_Module.generateHMAC(chunk) # TODO: save HMAC in traceker file
                ob = TLSender(payload= chunk, threadPoolExecutor = executor, remoteAddress = '192.168.0.105', remotePort =11111+i)
                # res = executor.map(ob.connectToRemoteServer, remotepassword='P@ssw0rd')
                ob.connectToRemoteServer(remotepassword='P@ssw0rd')
                # futs.append(ob.connectToRemoteServer(remotepassword='P@ssw0rd'))
                print("LOOP", i)
        with concurrent.futures.ProcessPoolExecutor() as multiProcessExecutor:
            hmac = HMAC_Module.generateHMAC(self.bufferObj.read(CHUNK_SIZE)) # TODO: save HMAC in traceker file
            # print( num_of_chunks / CHUNK_SIZE)
            # futures = {multiProcessExecutor.submit(P2PNetworkHandler, '192.168.106.75', 11111+i, self.bufferObj.read(CHUNK_SIZE)): i for i in range(0, int(num_of_chunks / CHUNK_SIZE))}

            # pprint.pprint(futures)
            # for future in concurrent.futures.as_completed(futures):
            #     ind = futures[future]
            #     # try:
            #     data = future.result()
            #     # except Exception as exc:
            #     #     print('%r generated an exception: %s' % (ind, exc))
            #     # else:
            #     #     print(ind, ' page is ',  data)

            # for i in range(0, int(num_of_chunks / CHUNK_SIZE)):
            #     # multiProcessExecutor.submit(P2PNetworkHandler, '192.168.106.75', 11111, self.bufferObj.read(CHUNK_SIZE))
            #     network_inst = P2PNetworkHandler(remoteAddr='192.168.106.75', port=11111, payload=self.bufferObj.read(CHUNK_SIZE))
                # network_inst.sendMode()
                # TODO: write tarckerr file
            print("done")
    # def read_chunk(self):
