import binascii
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from key_handling_module.key_handler import KeyHandler

class EncryptionService:

    # def __init__(self, key):
    #     

    @staticmethod
    def encrypt(inp: bytes):
        keyService = KeyHandler()
        aes = AES.new(keyService.key, AES.MODE_EAX)
        ciphertext, tag = aes.encrypt_and_digest(inp)
        encryptedList = [x for x in (aes.nonce, tag, ciphertext) ]
        print("cipher:", binascii.hexlify(ciphertext))
        print(encryptedList)
        return encryptedList

    @staticmethod
    def decrypt(encryptedList: bytes) -> bytes:
        (nonce, tag, ciphertext) = encryptedList
        keyService = KeyHandler()
        aes = AES.new(keyService.key, AES.MODE_EAX, nonce)
        data = aes.decrypt_and_verify(ciphertext, tag)
        print (data.decode("utf-8"))
