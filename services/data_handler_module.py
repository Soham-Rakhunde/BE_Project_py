import os, io
from ui.printer import Printer
from utils.constants import *
import ntpath

class DataHandler:
    file_path: str = None
    file_name: str = None
    data: bytes = None
    cipher: bytes = None
    AESNonce: bytes = None # Needed for decryption, Save with file
    MACtag: bytes = None   # Neeed for decryption, Save with file

    def __init__(self, file_path: str, filename):
        self.file_name = filename
        self.file_path = file_path
        self.printer = Printer()

    def read_file(self):
        with open(self.file_path, 'rb') as f:
            self.data = f.read()
            print("File Size:",len(self.data))



    '''pads the data for 32KB Chunk and stores in format:
        -> First 3 bytes for size of the pad
        -> then the pad (if any) 
        -> then the cipher 
        -> 16 bytes of AESNonce 
        -> 16 bytes of MACTag
    '''
    def encode_and_pad(self) -> io.BufferedIOBase: 
        self.printer.write(name='DataHandler', msg=f"Encoding and padding the Cipher, Nonce and MAC tag to form a buffer")
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


        # buffer.read(3)
        # buffer.read(3)

        print("Chunk size: ", CHUNK_SIZE)
        print("Pad size: ", PAD_SIZE)
        print("buffer size: ", buffer.getbuffer().nbytes)
        self.printer.write(name='DataHandler', msg=f"Cipher size: {len(self.cipher)} Bytes")
        self.printer.write(name='DataHandler', msg=f"Pad size: {PAD_SIZE} Bytes")
        self.printer.write(name='DataHandler', msg=f"Buffer size: {buffer.getbuffer().nbytes} Bytes")
        return buffer
        
    def decode(self, buffer: io.BytesIO):
        print(type(buffer), buffer.getbuffer().nbytes)
        self.printer.write(name='DataHandler', msg=f"Decoding buffer to extract Cipher, Nonce and Mac tag of size {buffer.getbuffer().nbytes} Bytes")
        
        buffer.seek(0)
        pad_size_bin = buffer.read1(3)
        PAD_SIZE = int.from_bytes(pad_size_bin, byteorder ='big')
        

        buffer.read1(PAD_SIZE)
        print("PAD_SIZE", PAD_SIZE)
        
        CIPHER_SIZE = buffer.getbuffer().nbytes - 16 - 16 - 3 - PAD_SIZE
        self.cipher = buffer.read1(CIPHER_SIZE)
        self.AESNonce = buffer.read1(16)
        self.MACtag = buffer.read1(16)
        print("CIPHER: ", CIPHER_SIZE, " ",len(self.cipher))
        print("AESNonce: ",len(self.AESNonce))
        print("MACtag: ",len(self.MACtag))
        self.printer.write(name='DataHandler', msg=f"Cipher size retrieved: {len(self.cipher)} Bytes")
        self.printer.write(name='DataHandler', msg=f"AESNonce size retrieved: {len(self.AESNonce)} Bytes")
        self.printer.write(name='DataHandler', msg=f"MACtag size retrieved: {len(self.MACtag)} Bytes")


    def write_file(self, save_path = 'C:\\Users\\soham\\OneDrive\\Desktop\\3433.jpg'):
        # TODO ask for file path
        with open(save_path, 'wb') as f:
            f.write(self.data)
        print(os.path.exists(save_path))
        print("File saved at", save_path)
        self.printer.write(name='DataHandler', msg=f"File saved at {save_path}")