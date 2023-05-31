#################################################################################################################################################################
# References
#   Generating self-signed certificate     https://cryptography.io/en/latest/x509/tutorial/
#   RSA Cryptography                       https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
#   TLS/SSL secured socket                 https://docs.python.org/3/library/ssl.html
#   Multithreading                         https://realpython.com/intro-to-python-threading/


# Items necessary to perform operations with private/public keys
from concurrent.futures import ThreadPoolExecutor
import threading
from services.hmac_module import HMAC_Module
from ui.dataAccumlator import DataLogger
from ui.printer import Printer
from utils.constants import CHUNK_SIZE, TLS_MAX_SIZE
from utils.socket_util_functions import receiveLocationsList, receivePayload, sendLocationsList, sendMsg
from utils.tls_util_functions import *

# Python server/client module, as well as ssl module to wrap the socket in TLS
import socket
import ssl

# Detecting whether the script is running in Windows or otherwise by importing the msvcrt module
# try:
#     import msvcrt
#     win = 1
# except:
#     win = 0

# GUI inports
# import tkinter as tk    #Standard python GUI library
import re  # For user input validations

# For managing the self-signed cert, and incoming public certificates
import os


class HostTLSInterface:
    # Local is Client here
    # Remote is Server here
    # As server listens to client connections to receive data from clients(Sender)
    # if retrieval Mode this will work as receiver

    localClientAddress = None
    remServerAddress: str = None
    localPort: int = None
    remotePort: int = None
    remPublicKey = None
    timeout: int = 0
    retreivalMode: bool = False
    localRedundancyCount = 2  # TODO
    locationsList: list = None
    hmac: str = None
    chunkId: int = None

    threadPoolExecutor: ThreadPoolExecutor = None
    payload: bytes = None

    clientSocket: ssl.SSLSocket = None

    hashingAlgorithm = hashes.SHA512()
    passwd_hashingAlgorithm = hashes.SHA256()
    passwd_attempts = 4
    BufferSize = 1024
    retrievalMode = False  # if true then it works as a receiver

    def __init__(
        self,
        threadPoolExecutor: ThreadPoolExecutor,
        remoteAddress: str,
        remotePort: int,
        payload: bytes = None,
        retrievalMode: bool = False,
        locationsList: list = None,
        hmac: str = None,
        chunkId: int = None,
        peerId: int = None,
    ):
        self.remServerAddress = remoteAddress
        self.threadPoolExecutor = threadPoolExecutor
        self.payload = payload
        self.remotePort = remotePort
        self.retrievalMode = retrievalMode
        self.locationsList = locationsList
        self.hmac = hmac
        self.chunkId = chunkId
        self.printer = Printer()
        self.uiDataLogs = DataLogger()
        self.peerId = peerId

    def printMsg(self, msg, name=""):
        name = ":"+name
        self.printer.write(
            name=f"Thread-{self.threadName}:Chunk-{self.chunkId}{name if name != ':' else ''}",
            msg=msg,
            log_name="hostInterface"
        )

    def connectToRemoteServer(self, networkPassword):
        self.threadName = threading.get_native_id()
        self.uiDataLogs.write(threadID=self.threadName, chunkId=self.chunkId, peer_id=self.peerId, peer_addr=self.remServerAddress, locationList=self.locationsList)
        self.printMsg(
            msg=f"Attempting connection to IP address: {self.remServerAddress}")
        # TLS server context
        clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
        # Attempt to connect to a remote address with a regular socket

        # Ignore timeout errors and continually attempt to connect until it succeeds
        maxTries = self.remotePort + 20
        while self.remotePort < maxTries:
            print(
                f"C: Attempting connection to remServerAddress:{self.remServerAddress} remotePort {self.remotePort}...")
            try:
                self.remServerAddress = self.remServerAddress.split(' ')[0]
                clientSocketI = socket.create_connection(
                    (self.remServerAddress, self.remotePort))
                break
            except TimeoutError:
                pass
            except ConnectionAbortedError:
                print('C: A connection was established, but then refused by the host')
                # self.remotePort += 1
            except OSError as e:
                print('C: No route found found to host,', e)
                # self.remotePort += 1
        # After connection, secure the socket
        self.clientSocket = clientContext.wrap_socket(
            clientSocketI, server_hostname=self.remServerAddress)
        # Pass that socket up to the global scope pefore the therad ends, so that the main function can utilize it
        print(
            f"C: Connection established to remServerAddress:{self.remServerAddress}:{self.remotePort}")

        self.printMsg(
            msg=f"Connection established to IP address: {self.remServerAddress}",)
        # Get remote address and certificate to validate if a cert is good or not
        raddr = self.clientSocket.getpeername()[0]
        rcert = self.clientSocket.getpeercert(True)

        # Clean the remote address to use as a filename when storing remote public cert to disk
        raddr = re.sub(r'[^a-zA-Z0-9\.]', '', raddr)
        # If there isn't currently a cert stored for the address, write to disk
        if not os.path.isfile(f'RemoteCerts/{raddr}'):
            fp = open(f'RemoteCerts/{raddr}', 'wb')
            fp.write(bytearray(b for b in rcert))
            fp.close()
            print(f"C: {raddr} added to known hosts")

        # If it does exist, read its contents and compare it to the just retrieved one
        else:
            fp = open(f'RemoteCerts/{raddr}', 'rb')
            storedCert = b''
            for c in fp:
                storedCert += c
            fp.close()

            if storedCert == rcert:
                print(f'C: {raddr} identity is the same')
            else:
                print(
                    f'C: ALERT - {raddr} identity has changed\t <-------------------')

        self.clientSocket.settimeout(None)

        # Exit if nothing was returned
        if self.clientSocket is None:
            print("C: no socket initailised, exiting")
            return

        # Recieve public key, then send back an encrypted password attempt with it
        pubkey = self.clientSocket.recv(self.BufferSize)
        self.remPublicKey = readPub(pubkey)
        print("C: Recieved public key from remote server")
        self.printMsg(msg="Recieved Peer's Public key")

        print(verifyCert(remPubKey=pubkey, remCert=rcert))

        self.printMsg(msg="Succesfully verified Peer Certificate")

        h = hashes.Hash(self.passwd_hashingAlgorithm,
                        backend=default_backend())
        h.update(bytes(networkPassword, 'utf8'))
        remotePasswordHash = h.finalize()

        attempts = 0
        while attempts < self.passwd_attempts:
            # Send password attempt
            self.clientSocket.send(
                encrypt(self.remPublicKey, remotePasswordHash))
            print("C: Sent password attempt")

            self.printMsg(
                msg="Sending Password attempt to verify legiblity of peer")

            # Then wait for a response and act on it
            response = self.clientSocket.recv(self.BufferSize)
            if response == b'Granted':
                print("C: Password accepted by remote host")
                self.printMsg(msg="Password accepted by remote host")

                self.passAuth = True
                break
            else:
                print("C: Password rejected by remote host")
                self.printMsg(msg="Password rejected by remote host")
                return
                # attempts += 1
                # if attempts < self.passwd_attempts:
                #     # Provide a tkinter input if running gui, or exit the program on wrong attempt
                #     if not self.args:
                #         networkPassword = self.passwordWindow()
                #         if not networkPassword:
                #             self.clientSocket.close()
                #             return
                #     else:
                #         self.clientSocket.close()
                #         return
                #     if networkPassword == None:
                #         return

        # Exit if client authentication failed
        if not self.passAuth:
            return

        # Symmetric Key Exchange
        # Generate and send it out via the remote public key
        # symmkeyLocal = Fernet.generate_key()
        # self.printMsg
        #
        #     msg="Generated Symmetric 128-bit Session key",
        #
        # )
        # self.clientSocket.send(encrypt(self.remPublicKey, symmkeyLocal))
        # # symmkeyCypherSuite= Fernet(symmkeyLocal)
        # print(f"C: Sent symmetric key to {self.remServerAddress}")

        # self.printMsg
        #
        #     msg=f"Sent symmetric key to {self.remServerAddress}",
        #
        # )

        if self.retrievalMode:
            sendMsg(socket=self.clientSocket, msg="RetrievalMode")
            self.uiDataLogs.update(peer_id=self.peerId, status="Mode msg sent")
            self.printMsg(
                msg="Sending selected mode i.e. Retrieval Mode to peer")

            print("C: (RetrievalMode): sending locations list")
            print("C: (RetrievalMode)", self.locationsList)
            sendLocationsList(socket=self.clientSocket,
                              locationList=self.locationsList)

            self.printMsg(msg="sending locations list to peer")
            self.uiDataLogs.update(peer_id=self.peerId, status="Locations sent")

            # try until we have locations left at peer by sending sendmsg
            tryNumber = 0
            while True:
                self.payload = receivePayload(socket=self.clientSocket)
                if self.payload.getbuffer().nbytes != CHUNK_SIZE:
                    print("C: (retrievalMode) Data has been deleted at peer")
                    self.printMsg(msg="Data has been deleted at peer")
                    break

                valid = HMAC_Module.verifyHMAC(
                    msg=self.payload.getvalue(),
                    hmac=self.hmac
                )
                if valid:
                    print(
                        "HMAC Checker: Succesfully verified the chunk for integrity and authenticity for chunk", self.chunkId)
                    self.printMsg(
                        name="HMAC Service", msg="Succesfully verified the chunk for integrity and authenticity")
                    self.uiDataLogs.update(peer_id=self.peerId, status="Integrity verified")
                    break
                else:
                    tryNumber += 1
                    print(
                        "HMAC Checker: The data is corrupted or wrong key provided for chunk", self.chunkId)
                    self.printMsg(name="HMAC Service",msg="The data is corrupted or wrong key provided for chunk")
                    if tryNumber < len(self.locationsList):
                        print("C: Requesting chunk", self.chunkId,
                              ' from the same peer try-', 1+tryNumber)
                        self.printMsg(msg=str("Requesting chunk "+str(self.chunkId)+' from the same peer try-' + str(1+tryNumber)),)
                        self.uiDataLogs.update(peer_id=self.peerId, status="Corrupt Data received, Retrying")
                        sendMsg(socket=self.clientSocket, msg=str(tryNumber))
                    else:  # data not found at peer, emptying the payload data as it will be returned outside
                        self.payload.seek(0)
                        self.payload.truncate()
                        self.uiDataLogs.update(peer_id=self.peerId, status="Cancelled: Chunks not found/corrupted")
                        break

            sendMsg(socket=self.clientSocket, msg="END")
            self.clientSocket.close()
            self.uiDataLogs.update(peer_id=self.peerId, status="Succesful")
            print("C: (retrievalMode) Transaction complete, Ending connection")
            self.printMsg(msg="Transaction complete; Ending connection")
            return self.payload
        else:
            sendMsg(socket=self.clientSocket, msg="StorageMode")
            self.uiDataLogs.update(peer_id=self.peerId, status="Mode msg sent")
            self.printMsg(msg="Sending selected mode i.e. Storage Mode to peer")

            print("C: (storageMode) Sending the Payload")
            self.clientSocket.send(self.payload)
            self.printMsg(msg="Chunk sent of 512KB")

            print("C: (storageMode): receiving locations to store at tracker")
            self.locationsList = receiveLocationsList(
                socket=self.clientSocket, BufferSize=self.BufferSize)
            
            self.uiDataLogs.update(peer_id=self.peerId ,locationList=self.locationsList)

            self.printMsg(msg="Received locations where chunk is hidden at peer to store at tracker")
            print("C: (storageMode) ", self.locationsList)
            self.clientSocket.close()
            print("C: (retrievalMode) Transaction complete, Ending connection")
            self.printMsg(msg="Transaction complete; Ending connection")
            return self.locationsList
