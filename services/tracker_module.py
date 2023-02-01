import io
from utils.constants import *
from services.data_handler_module import DataHandler


class Tracker:
    bufferObj: io.BufferedIOBase = None

    def __init__(self, bufferObj: io.BufferedIOBase) -> None:
        self.bufferObj = bufferObj

    def send_chunks(self):
        # TODO call p2pnetworkhandler for each chunk
        self.bufferObj.seek(0)
        num_of_chunks = self.bufferObj.getbuffer().nbytes
        for i in range(0, num_of_chunks % CHUNK_SIZE):
            print(len(self.bufferObj.read(CHUNK_SIZE)))
