from Crypto.Cipher import AES
from services.data_handler_module import DataHandler
from services.key_handling_module import KeyHandler
from ui.printer import Printer

class EncryptionService:

    @staticmethod
    def encrypt(_dataHandler: DataHandler):
        keyService = KeyHandler()
        printer = Printer()
        
        aes = AES.new(keyService.key, AES.MODE_EAX)
        _dataHandler.AESNonce = aes.nonce
        _dataHandler.cipher, _dataHandler.MACtag = aes.encrypt_and_digest(_dataHandler.data)
        printer.write("Encryption Service", 'Encrypted data with AES with 128 bit key in EAX (Block cipher method for Authenticated Encryption with Associated Data (AEAD) algorithm) mode')
        # print(len(aes.nonce), len(_dataHandler.MACtag))

    @staticmethod
    def decrypt(_dataHandler: DataHandler):
        keyService = KeyHandler()
        aes = AES.new(keyService.key, AES.MODE_EAX, _dataHandler.AESNonce)

        printer = Printer()
        _dataHandler.data = aes.decrypt_and_verify(_dataHandler.cipher, _dataHandler.MACtag)
        printer.write("Decyption Service", 'Decryped and verified data with AES with 128 bit key in EAX (Block cipher method for Authenticated Encryption with Associated Data (AEAD) algorithm) mode')
        # print (data.decode("utf-8"))