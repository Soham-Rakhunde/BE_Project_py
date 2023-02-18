import base64
from Crypto.Hash import HMAC, SHA256

from services.key_handling_module import KeyHandler

class HMAC_Module:

    @staticmethod
    def generateHMAC(msg: bytes) -> str:
        keyHandler = KeyHandler()

        h = HMAC.new(keyHandler.key, digestmod=SHA256)
        h.update(msg)
        hmac = h.digest() # for string use hexdigest instead
        encodedHMACstr = base64.b64encode(hmac).decode("ascii")
        return encodedHMACstr
    
    @staticmethod
    def verifyHMAC(msg: bytes, hmac:str):
        decodedHMAC = base64.b64decode(hmac.encode('ascii'))
        keyHandler = KeyHandler()

        h = HMAC.new(key=keyHandler.key, msg=msg, digestmod=SHA256)
        try:
            h.verify(decodedHMAC)  # for string use hexverify instead
            return True
        except ValueError:
             return False