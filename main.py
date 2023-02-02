from services.encrypt_module import EncryptionService
from services.data_handler_module import DataHandler
from services.partitioning_module import Partitioner
from services.network_services.p2p_network_handler import P2PNetworkHandler
import base64

if __name__ == "__main__":
    # TODO input file path
    _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    EncryptionService.encrypt(_dataHandler)
    Partitioner.partition(_dataHandler)
    EncryptionService.decrypt(_dataHandler)
    _dataHandler.write_file()

    # tracker = P2PNetworkHandler()