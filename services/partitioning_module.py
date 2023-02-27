import io
import pprint
from services.data_handler_module import DataHandler
from ui.printer import Printer
from utils.constants import *


''' Instead of Partioner '''
class Partitioner:

    @staticmethod
    def partition(_dataHandler: DataHandler) -> io.BytesIO:
        bufferObj = _dataHandler.encode_and_pad()
        # del _dataHandler
        print(CHUNK_SIZE)
        # bufferObj.seek(0)
        # num_of_chunks = bufferObj.getbuffer().nbytes
        # for i in range(0, int(num_of_chunks / CHUNK_SIZE)):
        #     print(len(bufferObj.read(CHUNK_SIZE)))

        return bufferObj
    
    @staticmethod
    def merge(bufferDictionary: dict) -> io.BytesIO:
        sorted_buffers = sorted(bufferDictionary.items(), key=lambda x: x[1])

        sorted_buffers = [b[0].result() for b in sorted_buffers]
        # pprint.pprint(sorted_buffers)


        buffer = io.BytesIO()
        for bytesIObj in sorted_buffers:
            buffer.write(bytesIObj.getvalue())

        print(buffer.getbuffer().nbytes)
        return buffer


        