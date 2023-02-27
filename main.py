from services.network_services.peerTLSInterface import PeerTLSInterface
from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from retrieval_module import RetrieverModule
from services.encrypt_module import EncryptionService
from services.data_handler_module import DataHandler
from services.hmac_module import HMAC_Module
from services.partitioning_module import Partitioner

from services.tracker_module import Tracker

def sender():
    # TODO input file path
    _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    _dataHandler.read_file()
    EncryptionService.encrypt(_dataHandler)
    buffer = Partitioner.partition(_dataHandler)
    print("Tracker")
    tracker = Tracker(bufferObj=buffer)
    tracker.send_chunks()

def retriever():
    ret = RetrieverModule(tracker_path='Temp/tracker.json')
    ret.retrieve()

def act_as_peer():
    ob = PeerTLSInterface(remoteAddress = '192.168.0.103', localPort= 11111)
    ob.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')



if __name__ == "__main__":
    # discovery = DiscoveryServiceInterface()
    sender()