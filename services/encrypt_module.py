import binascii
from Crypto.Cipher import AES
from services.data_handler_module import DataHandler
# from Crypto.Random import get_random_bytes
from services.key_handling_module import KeyHandler

class EncryptionService:

    @staticmethod
    def encrypt(_dataHandler: DataHandler):
        keyService = KeyHandler()
        aes = AES.new(keyService.key, AES.MODE_EAX)
        _dataHandler.AESNonce = aes.nonce
        _dataHandler.cipher, _dataHandler.MACtag = aes.encrypt_and_digest(_dataHandler.data)
        # print(len(aes.nonce), len(_dataHandler.MACtag))

    @staticmethod
    def decrypt(_dataHandler: DataHandler) -> bytes:
        keyService = KeyHandler()
        aes = AES.new(keyService.key, AES.MODE_EAX, _dataHandler.AESNonce)

        _dataHandler.data = aes.decrypt_and_verify(_dataHandler.cipher, _dataHandler.MACtag)
        # print (data.decode("utf-8"))