from encrypt_module.encryptor import EncryptionService
from data_module.data_handler import DataHandler
from partitioning_module.partitioner import Partitioner
import base64

if __name__ == "__main__":
    # TODO input file path
    _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    EncryptionService.encrypt(_dataHandler)
    Partitioner.partition(_dataHandler)
    # EncryptionService.decrypt(_dataHandler)
    # _dataHandler.write_file()