from encrypt_module.encryptor import EncryptionService
from data_module.data_handler import DataHandler
import base64

if __name__ == "__main__":
    # TODO input file path
    dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    cipher = EncryptionService.encrypt(dataHandler)
    print("Decrypt:")
    EncryptionService.decrypt(dataHandler)
    dataHandler.write_file()