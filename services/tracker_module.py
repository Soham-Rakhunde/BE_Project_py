import io
from services.hmac_module import HMAC_Module
from services.network_services.p2p_network_handler import P2PNetworkHandler
from utils.constants import *


class Tracker:
    bufferObj: io.BufferedIOBase = None

    def __init__(self, bufferObj: io.BufferedIOBase) -> None:
        self.bufferObj = bufferObj

    def send_chunks(self):
        # TODO call p2pnetworkhandler for each chunk
        self.bufferObj.seek(0)
        num_of_chunks = self.bufferObj.getbuffer().nbytes
        for i in range(0, num_of_chunks % CHUNK_SIZE):
            hmac = HMAC_Module.generateHMAC(self.bufferObj.read(CHUNK_SIZE)) # TODO: save HMAC in traceker file
            network_inst = P2PNetworkHandler(remoteAddr='192.168.106.75', port=11111, payload=self.bufferObj.read(CHUNK_SIZE))
            network_inst.sendMode()
            # TODO: write tarckerr file
            
    # def read_chunk(self):
