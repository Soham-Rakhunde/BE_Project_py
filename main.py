from services.encrypt_module import EncryptionService
from services.data_handler_module import DataHandler
from services.key_handling_module import KeyHandler
from services.partitioning_module import Partitioner
from services.network_services.p2p_network_handler import P2PNetworkHandler
import base64

from services.tracker_module import Tracker

if __name__ == "__main__":
    # TODO input file path
    _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
    EncryptionService.encrypt(_dataHandler)
    buffer = Partitioner.partition(_dataHandler)
    print("Tracker")
    tracker = Tracker(bufferObj=buffer)
    tracker.send_chunks()
    # EncryptionService.decrypt(_dataHandler)
    # _dataHandler.write_file()
    # import urllib.request

    # external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    # print(external_ip)

    # tracker = P2PNetworkHandler()

# import concurrent.futures
# from concurrent.futures import ProcessPoolExecutor
# import urllib.request, pprint

# URLS = ['http://www.foxnews.com/',
#    'http://www.cnn.com/',
#    'http://europe.wsj.com/',
#    'http://www.bbc.co.uk/',
#    'http://some-made-up-domain.com/']

# def load_url(url, timeout):
#     with urllib.request.urlopen(url, timeout = timeout) as conn:
#         return conn.read()

# def main():
#     with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
#         future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
#         pprint.pprint(future_to_url)
#         for future in concurrent.futures.as_completed(future_to_url):
#             url = future_to_url[future]
#             try:
#                 data = future.result()
#             except Exception as exc:
#                 print('%r generated an exception: %s' % (url, exc))
#             else:
#                 print('%r page is %d bytes' % (url, len(data)))

# if __name__ == '__main__':
#     main()