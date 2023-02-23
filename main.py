from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from retrieval_module import RetrieverModule
from services.encrypt_module import EncryptionService
from services.data_handler_module import DataHandler
from services.hmac_module import HMAC_Module
from services.partitioning_module import Partitioner
import base64

from services.tracker_module import Tracker

if __name__ == "__main__":
    
    discovery = DiscoveryServiceInterface()


    # TODO input file path
    # _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    # _dataHandler.read_file()
    # EncryptionService.encrypt(_dataHandler)
    # buffer = Partitioner.partition(_dataHandler)
    # print("Tracker")
    # tracker = Tracker(bufferObj=buffer)
    # tracker.send_chunks(_dataHandler)

    ret = RetrieverModule(tracker_path='Identity/tracker.json')
    ret.retrieve()
