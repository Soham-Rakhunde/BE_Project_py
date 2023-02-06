#################################################################################################################################################################
#References
#   Generating self-signed certificate     https://cryptography.io/en/latest/x509/tutorial/
#   RSA Cryptography                       https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
#   TLS/SSL secured socket                 https://docs.python.org/3/library/ssl.html
#   Multithreading                         https://realpython.com/intro-to-python-threading/


#Items necessary to perform operations with private/public keys
from concurrent.futures import ThreadPoolExecutor
from utils.tls_util_functions import *

#Symmetric key generation
import cryptography.fernet
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

#GUI inports
# import tkinter as tk    #Standard python GUI library
import re               #For user input validations

#For managing the self-signed cert, and incoming public certificates
import os

class TLSender:
    # Local is Client here
    # Remote is Server here
    # As server listens to client connections to receive data from clients(Sender)

    localClientAddress = None
    remServerAddress: str = None
    localPort: int = None
    remotePort: int = None
    remPublicKey = None
    timeout: int = 0


    threadPoolExecutor: ThreadPoolExecutor = None
    payload: bytes = None

    clientSocket: ssl.SSLSocket = None

    
    hashingAlgorithm = hashes.SHA512()
    passwd_hashingAlgorithm = hashes.SHA256()
    passwd_attempts = 4
    BufferSize = 1024

    def __init__(self, payload: bytes, threadPoolExecutor: ThreadPoolExecutor, remoteAddress: str, remotePort: int):
        self.remServerAddress = remoteAddress
        self.threadPoolExecutor = threadPoolExecutor
        self.payload = payload
        self.remotePort = remotePort

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
        fut = self.threadPoolExecutor.submit(self.authenticateAndSend, remotepassword)
        # print(fut.result())

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
        print("C: Done")
        self.sendData()
        return "YES DONE"
        # return {
        #     'localS':remoteSocket,
        #     'remoteS':self.c_socket[0],
        #     'localK':symmkeyLocal,
        #     'remoteK':symmkeyRemote
        # }



    def sendData(self):
        print("C: sending payload")
        self.clientSocket.send(bytes(self.payload,'utf-8'))
        # self.peerMAC = self.recieveSocket.recv() TODO: receive the loacation
        self.clientSocket.close()
        print("Closing sockets")
        # return