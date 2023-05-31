import os
from base64 import b64encode
from utils.singleton_meta import SingletonMeta
from Crypto.Random import get_random_bytes
import pyargon2

class KeyHandler(metaclass=SingletonMeta):
    key: bytes = None # Key size is 32 Bytes
    salt: str = None # Salt size is 64 Bytes

    SALT_SIZE = 64
    KEY_SIZE = 32

    # file_name: str = 'key_n_salt.bin'
    # TODO ONLY SAVE the salt
    # path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + file_name
    path = 'Identity/salt.bin'

    @staticmethod
    def is_password_created():
        return os.path.exists('Identity/salt.bin')

    def __init__(self):
        if not os.path.isdir('Identity'):
            os.mkdir('Identity')

        if os.path.exists(self.path):
            self.retrieve()
            # print("key retrieved:", self.path)
        else:
            self.generate(password="passsasedw")
            self.save()

    def generate(self, password: str):
        self.salt = get_random_bytes(self.SALT_SIZE)
        self.key = pyargon2.hash(password, str(b64encode(self.salt)), hash_len=self.KEY_SIZE, encoding='raw')
        # self.key = PBKDF2(password.encode("utf8"), self.salt, 32, count=1000000, hmac_hash_module=SHA512)
        # print("Derived key:", binascii.hexlify(self.key))


# TODO remove key and ask password everytime to derive the key

    def save(self):
        with open(self.path, 'wb') as file:
            file.write(self.key)
            file.write(self.salt)

    def retrieve(self):
        with open(self.path, 'rb') as file:
            self.key = file.read(32)
            self.salt = file.read(64)
            self.salt = str(b64encode(self.salt))



class KeyHandlerUI(metaclass=SingletonMeta):
    key: bytes = None # Key size is 32 Bytes
    salt: str = None # Salt size is 64 Bytes

    SALT_SIZE = 64
    KEY_SIZE = 32

    # file_name: str = 'key_n_salt.bin'
    # TODO ONLY SAVE the salt
    # path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + file_name
    path = 'Identity/salt.bin'

    @staticmethod
    def is_password_created():
        return os.path.exists('Identity/salt.bin')

    def __init__(self):
        if not os.path.isdir('Identity'):
            os.mkdir('Identity')
        # if not os.path.exists(self.path): commmenting this as salt can be creeateed later
        #     self.generateSalt()
    
    def is_password_created(self):   
        print(os.path.exists(self.path))
        return os.path.exists(self.path)

    def generateSalt(self):
        self.salt = get_random_bytes(self.SALT_SIZE)
        with open(self.path, 'wb') as file:
            file.write(self.salt)
    
    def generateKey(self, password: str):
        self.generateSalt()
        self.key = pyargon2.hash(password, str(b64encode(self.salt)), hash_len=self.KEY_SIZE, encoding='raw')

    def retrieve(self, password:str):
        with open(self.path, 'rb') as file:
            self.salt = file.read(64)
            # self.salt = str(b64encode(self.salt))
            self.key = pyargon2.hash(password, str(b64encode(self.salt)), hash_len=self.KEY_SIZE, encoding='raw')
