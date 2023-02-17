#################################################################################################################################################################
#References
#   Generating self-signed certificate     https://cryptography.io/en/latest/x509/tutorial/
#   RSA Cryptography                       https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
#   TLS/SSL secured socket                 https://docs.python.org/3/library/ssl.html
#   Multithreading                         https://realpython.com/intro-to-python-threading/


#Items necessary to perform operations with private/public keys
from concurrent.futures import ThreadPoolExecutor
from utils.socket_util_functions import receiveLocationsList, receivePayload, sendLocationsList, sendMsg
from utils.tls_util_functions import *

#Symmetric key generation
from cryptography.fernet import Fernet

#Python server/client module, as well as ssl module to wrap the socket in TLS
import socket
import ssl

#Detecting whether the script is running in Windows or otherwise by importing the msvcrt module
try:
    import msvcrt
    win=1
except:
    win=0

import re               #For user input validations

#For managing the self-signed cert, and incoming public certificates
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
    localRedundancyCount = 2 # TODO
    locationsList: list = None


    threadPoolExecutor: ThreadPoolExecutor = None
    payload: bytes = None

    clientSocket: ssl.SSLSocket = None

    
    hashingAlgorithm = hashes.SHA512()
    passwd_hashingAlgorithm = hashes.SHA256()
    passwd_attempts = 4
    BufferSize = 1024
    retrievalMode = False # if true then it works as a receiver

    def __init__(self, threadPoolExecutor: ThreadPoolExecutor, remoteAddress: str, remotePort: int, payload: bytes = None, retrievalMode: bool=False, locationsList: list= None):
        self.remServerAddress = remoteAddress
        self.threadPoolExecutor = threadPoolExecutor
        self.payload = payload
        self.remotePort = remotePort
        self.retrievalMode = retrievalMode
        self.locationsList = locationsList

    def connectToRemoteServer(self, remotepassword):
        #TLS server context
        clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
        #Attempt to connect to a remote address with a regular socket
        
        #Ignore timeout errors and continually attempt to connect until it succeeds
        maxTries = self.remotePort + 20
        while self.remotePort < maxTries:
            print(f"C: Attempting connection to remServerAddress:{self.remServerAddress} remotePort {self.remotePort}...")
            try:
                clientSocketI = socket.create_connection((self.remServerAddress, self.remotePort))
                break
            except TimeoutError:
                pass
            except ConnectionAbortedError:
                print('C: A connection was established, but then refused by the host')
                # self.remotePort += 1
            except OSError as e:
                print('C: No route found found to host,', e)
                # self.remotePort += 1
        #After connection, secure the socket
        self.clientSocket = clientContext.wrap_socket(clientSocketI, server_hostname=self.remServerAddress)
        #Pass that socket up to the global scope pefore the therad ends, so that the main function can utilize it
        print(f"C: Connection established to remServerAddress:{self.remServerAddress}:{self.remotePort}")
        future = self.threadPoolExecutor.submit(self.authenticateAndSend, remotepassword)
        return future

    def authenticateAndSend(self, remotepassword):
        print("C: Thread Spawned")
        #Get remote address and certificate to validate if a cert is good or not
        raddr = self.clientSocket.getpeername()[0]
        rcert = self.clientSocket.getpeercert(True)

        #Clean the remote address to use as a filename when storing remote public cert to disk
        raddr = re.sub(r'[^a-zA-Z0-9\.]','',raddr)
        #If there isn't currently a cert stored for the address, write to disk
        if not os.path.isfile(f'RemoteCerts/{raddr}'):
            fp = open(f'RemoteCerts/{raddr}','wb')
            fp.write(bytearray(b for b in rcert))
            fp.close()
            print(f"C: {raddr} added to known hosts")
        
        #If it does exist, read its contents and compare it to the just retrieved one
        else:
            fp = open(f'RemoteCerts/{raddr}','rb')
            storedCert = b''
            for c in fp:
                storedCert += c
            fp.close()

            if storedCert == rcert:
                print(f'C: {raddr} identity is the same')
            else:
                print(f'C: ALERT - {raddr} identity has changed\t <-------------------')

        self.clientSocket.settimeout(None)



        #Exit if nothing was returned
        if self.clientSocket is None:
            print("C: no socket initailised, exiting")
            return


        #Recieve public key, then send back an encrypted password attempt with it
        pubkey = self.clientSocket.recv(self.BufferSize)
        self.remPublicKey = readPub(pubkey)
        print("C: Recieved public key from remote server")

        print(verifyCert(remPubKey=pubkey, remCert=rcert))

        h = hashes.Hash(self.passwd_hashingAlgorithm,backend=default_backend())
        h.update(bytes(remotepassword,'utf8'))
        remotePasswordHash = h.finalize()

        attempts = 0
        while attempts < self.passwd_attempts:
            #Send password attempt
            self.clientSocket.send(encrypt(self.remPublicKey, remotePasswordHash))
            print("C: Sent password attempt")

            #Then wait for a response and act on it
            response = self.clientSocket.recv(self.BufferSize)
            if response == b'Granted':
                print("C: Password accepted by remote host")
                self.passAuth = True
                break
            else:
                print("C: Password rejected by remote host")
                attempts += 1
                if attempts < self.passwd_attempts:
                    #Provide a tkinter input if running gui, or exit the program on wrong attempt
                    if not self.args:
                        remotepassword = self.passwordWindow()
                        if not remotepassword:
                            self.clientSocket.close()
                            return
                    else:
                        self.clientSocket.close()
                        return
                    if remotepassword == None:
                        return


        #Exit if client authentication failed
        if not self.passAuth:
            return

        #Symmetric Key Exchange
        #Generate and send it out via the remote public key
        symmkeyLocal = Fernet.generate_key()
        self.clientSocket.send(encrypt(self.remPublicKey, symmkeyLocal))
        # symmkeyCypherSuite= Fernet(symmkeyLocal)
        print(f"C: Sent symmetric key to {self.remServerAddress}")

        
        if self.retrievalMode:
            sendMsg(socket=self.clientSocket, msg="RetrievalMode")
            print("C: (RetrievalMode): sending locations list")
            print("C: (RetrievalMode)",self.locationsList)
            sendLocationsList(socket=self.clientSocket, locationList=self.locationsList)
            self.payload = receivePayload(socket=self.clientSocket)
            self.clientSocket.close()
            print("Sockets closed successfully")
            return 
        else:
            sendMsg(socket=self.clientSocket, msg="StorageMode")
            print("C: (not retrievalMode) Sending the Payload")
            self.clientSocket.send(self.payload)
            print("C: (not retreivalMode): receiving locations to store at tracker")
            self.locationsList = receiveLocationsList(socket=self.clientSocket, BufferSize=self.BufferSize)
            print("C: (not retreivalMode) ", self.locationsList)
            return self.locationsList
