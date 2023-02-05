import os, io
from utils.constants import *

class DataHandler:
    file_path: str = None
    data: bytes = None
    cipher: bytes = None
    AESNonce: bytes = None # Needed for decryption, Save with file
    MACtag: bytes = None   # Neeed for decryption, Save with file

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.read_file()

    def read_file(self):
        with open(self.file_path, 'rb') as f:
            self.data = f.read()
            print("File Size:",len(self.data))



    '''pads the data for 512KB Chunk and stores in format:
        First 3 bytes for size of the pad
        -> then the pad (if any) 
        -> then the cipher 
        -> 16 bytes of AESNonce 
        -> 16 bytes of MACTag
    '''
    def encode_and_pad(self) -> io.BufferedIOBase: 
        PAD_SIZE = CHUNK_SIZE - (len(self.cipher) + 16 + 16 + 3) % CHUNK_SIZE
        if PAD_SIZE == CHUNK_SIZE:
            PAD_SIZE = 0


        pad_size_bin = PAD_SIZE.to_bytes(length=3, byteorder='big')
        # print(int.from_bytes(z, byteorder='big'))


        buffer = io.BytesIO()
        buffer.write(pad_size_bin)
        buffer.write((0).to_bytes(length=PAD_SIZE, byteorder='big'))
        buffer.write(self.cipher)
        buffer.write(self.AESNonce)
        buffer.write(self.MACtag)


        buffer.read(3)
        buffer.read(3)

        # print("Chunk size: ", CHUNK_SIZE)
        # print("Pad size: ", PAD_SIZE)
        # print("buffer size: ", buffer.getbuffer().nbytes)
        return buffer
        
    # def decode(self):
    # TODO decode and unpad and save in the object members

    def write_file(self, save_path = 'C:\\Users\\soham\\OneDrive\\Desktop\\3433.jpg'):
        # TODO ask for file path
        with open(save_path, 'wb') as f:
            f.write(self.data)
        print(os.path.exists(save_path))
        print("File saved at", save_path)