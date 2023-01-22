import os, binascii
from singleton_meta import SingletonMeta
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes

class KeyHandler(metaclass=SingletonMeta):
    key: bytes = None

    def __init__(self):
        # TODO if found in storage then retrieve else generate
        if self.key == None:
            self.generate(password="passsasedw")
        else:
            pass

    def generate(self, password: str):
        salt = get_random_bytes(64) 
        # TODO save key and salt
        self.key = PBKDF2(password.encode("utf8"), salt, 32, count=1000000, hmac_hash_module=SHA512)
        print("Derived key:", binascii.hexlify(self.key))
