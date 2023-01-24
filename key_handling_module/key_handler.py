import binascii, os
from singleton_meta import SingletonMeta
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes

class KeyHandler(metaclass=SingletonMeta):
    key: bytes = None # Key size is 32 Bytes
    salt: bytes = None # Salt size is 64 Bytes

    file_name: str = 'key_n_salt.bin'
    # TODO change path
    path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + file_name


    def __init__(self):
        if os.path.exists(self.path):
            self.retrieve()
            # print("key retrieved:", self.path)
        else:
            self.generate(password="passsasedw")
            self.save()

    def generate(self, password: str):
        self.salt = get_random_bytes(64) 
        self.key = PBKDF2(password.encode("utf8"), self.salt, 32, count=1000000, hmac_hash_module=SHA512)
        # print("Derived key:", binascii.hexlify(self.key))

    def save(self):
        with open(self.path, 'wb') as file:
            file.write(self.key)
            file.write(self.salt)

    def retrieve(self):
        with open(self.path, 'rb') as file:
            self.key = file.read(32)
            self.salt = file.read(64)
