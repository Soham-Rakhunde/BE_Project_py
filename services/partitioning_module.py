import io
from services.data_handler_module import DataHandler


''' Instead of Partioner '''
class Partitioner:

    @staticmethod
    def partition(_dataHandler: DataHandler) -> io.BufferedIOBase:
        CHUNK_SIZE = 512 * 1024 # 512 KB
        
        bufferObj = _dataHandler.encode_and_pad()
        del _dataHandler

        bufferObj.seek(0)
        num_of_chunks = bufferObj.getbuffer().nbytes
        for i in range(0, num_of_chunks % CHUNK_SIZE):
            print(len(bufferObj.read(CHUNK_SIZE)))

        return bufferObj