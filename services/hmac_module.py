from Crypto.Hash import HMAC, SHA256

from services.key_handling_module import KeyHandler

class HMAC_Module:

    @staticmethod
    def generateHMAC(msg: bytes) -> bytes:
        keyHandler = KeyHandler()

        h = HMAC.new(keyHandler.key, digestmod=SHA256)
        h.update(msg)
        hmac = h.digest() # for string use hexdigest instead
        return hmac
    
    @staticmethod
    def verifyHMAC(msg: bytes, hmac:bytes):
        keyHandler = KeyHandler()

        h = HMAC.new(keyHandler.key, digestmod=SHA256)
        try:
            h.verify(hmac)  # for string use hexverify instead
            print("The message '%s' is authentic" % msg)
        except ValueError:
            print("The message or the key is wrong")