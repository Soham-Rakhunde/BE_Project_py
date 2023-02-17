#################################################################################################################################################################
#References
#   Generating self-signed certificate     https://cryptography.io/en/latest/x509/tutorial/
#   RSA Cryptography                       https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
#   TLS/SSL secured socket                 https://docs.python.org/3/library/ssl.html
#   Multithreading                         https://realpython.com/intro-to-python-threading/


#Items necessary to perform operations with private/public keys
from concurrent.futures import ThreadPoolExecutor
import io
import pathlib
import pickle
import secrets
import string
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from utils.constants import CHUNK_SIZE, TLS_MAX_SIZE
from utils.socket_util_functions import receiveLocationsList, receiveMsg, receivePayload, sendLocationsList
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

#Multithreading for simultaneously sending and recieving messages
import threading


class RemoteTLSInterface:
    # Local is SERVER here - Receiver
    # Remote is CLIENT here - Sender
    # As server(receiver) listens to client connections to receive data from clients(Sender)
    # if retrieval Mode this will act as a sender instead

    localServerAddress = None
    remClientAddress: str = None
    localPort: int = None
    remotePort: int = None
    remPublicKey = None
    timeout: int = 0
    retrievalMode: bool = False
    localRedundancyCount = 2 # TODO
    locationsList: list = None

    threadPoolExecutor: ThreadPoolExecutor = None
    payload: bytes = None
 
    remClientSocket: ssl.SSLSocket = None  # as we maintrain remote clients socket as interface

    hashingAlgorithm = hashes.SHA512()
    passwd_hashingAlgorithm = hashes.SHA256()
    passwd_attempts = 4
    BufferSize = 1024

    def __init__(self, threadPoolExecutor: ThreadPoolExecutor, remoteAddress: str, localPort: int, retrievalMode:bool = False, locationsList: list= None):
        self.remClientAddress = remoteAddress
        self.threadPoolExecutor = threadPoolExecutor
        self.localPort = localPort
        self.retrievalMode = retrievalMode
        self.locationsList = locationsList

        #Create directories to house the host identity, and remote public certs
        if not os.path.isdir('Identity'):
            os.mkdir('Identity')
        if not os.path.isdir('RemoteCerts'):
            os.mkdir('RemoteCerts')
        #Generate self-signed certificate if it doesn't exist
        makeCert()

        #Check that the port number is above 1000, and that all other inputs have something there before proceeding
        if not type(localPort) == int:
            raise Exception("Port number must be an integer value >= 1000")
        elif localPort < 1000:
            raise Exception("Port number must be an integer value >= 1000")
        # else:
        #     #Create a context that doesn't go anywhere, just for making sure the key password is correct before proceeding
        #     try:
        #         dummycontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #         dummycontext.load_cert_chain('Identity/certificate.pem', 'Identity/private_key.pem',password=keypasswd)
        #     except:
        #         raise Exception("Incorrect cerificate password provided")

    def connectToRemoteClient(self, keypasswd,hostpassword,remotepassword):
        # TLS client socket object
        serverContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        serverContext.load_cert_chain('Identity/certificate.pem', 'Identity/private_key.pem', password=keypasswd)

        serverSocketI = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        serverSocket = serverContext.wrap_socket(serverSocketI, server_side=True)

        #Bind the server socket to localhost, and turn off timeout so it can listen forever
        try:
            # serverSocket.bind(('0.0.0.0', 0))
            # serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # self.localPort = serverSocket.getsockname()[1]
            serverSocket.bind(('0.0.0.0',self.localPort))
        except OSError:
            print("S: Likely serverPort already in use (Linux has a brief timeout between runs)")
            return
        serverSocket.settimeout(None)

        #The socket accept operation has doesn't seem to have a means of exiting once it's started. So I worked around this by
        #having this function running in a separate thread, which makes a connection to localhost 
        def exitCatchTM(localPort, timeout):
            #Hold here until timeout criteria is reached, then close the connection
            x = datetime.datetime.utcnow().timestamp()
            while (not ((datetime.datetime.utcnow().timestamp() - x) > timeout)) or not timeout:
                pass

            if serverSocket == None:
                print("Exiting Catch timeout", serverSocket) 
                dummysocket = socket.create_connection(('127.0.0.1', localPort))
                clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
                dummySocketS = clientContext.wrap_socket(dummysocket, server_hostname='127.0.0.1')
        
        def exitCatchKP(localPort):
            input()
            print("Exiting Catch KP", serverSocket) 
            if serverSocket == None:
                dummysocket = socket.create_connection(('127.0.0.1',localPort))
                clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
                dummySocketS = clientContext.wrap_socket(dummysocket, server_hostname='127.0.0.1')

        quitK = threading.Thread(target=exitCatchKP,args=(self.localPort,), daemon=True)
        quitK.start()
        quitT = threading.Thread(target=exitCatchTM,args=(self.localPort, self.timeout,), daemon=True)
        quitT.start()

        print(f"S: Listening on LocalServerPort {self.localPort} (Press Enter to exit)...")

        #Start listening for connection
        serverSocket.listen(1)
        remoteAddress = self.remClientAddress
        try:
            self.remClientSocket, self.remClientAddress = serverSocket.accept() 
        except ConnectionAbortedError:
            print("S: Connection Cancelled, or timed out")
            return
        print("S: Connected to client addre:", self.remClientAddress)
        #If the remote connection was localhost (operation cancelled), exit the script
        if self.remClientAddress[0] == '127.0.0.1':
            serverSocket.close()
            print("S: Connection Cancelled, or timed out")
            return
        if self.remClientAddress[0] != remoteAddress:
            serverSocket.close()
            print(f"S: Connection recieved from unexpected host ({self.remClientAddress[0]})")
            return

        print(f"S: Established connection from {self.remClientAddress[0]}")

        
        future = self.threadPoolExecutor.submit(self.authenticateAndReveive, hostpassword, keypasswd)
        return future

    def authenticateAndReveive(self, hostpassword, keypasswd):
        print("S: Thread Spawned")
        #Generate keypair for password exchange
        # key = makeKey()
        key = retrieveKey(passwd=keypasswd)
        print("S: Retrieved Keypair")

        #Hash the passwords before sending them over the wire
        h = hashes.Hash(self.passwd_hashingAlgorithm,backend=default_backend())
        h.update(bytes(hostpassword,'utf8'))
        hostPasswordHash = h.finalize()
        # h = hashes.Hash(self.passwd_hashingAlgorithm,backend=default_backend())
        # h.update(bytes(remotepassword,'utf8'))
        # remotepassword = h.finalize()

        #Send the other node the public key, then wait for password attempt
        self.remClientSocket.send(pubString(key['public']))
        print(f"S: Sent public key to {self.remClientAddress[0]}")

        #If the password matches, send a Granted message. Else send denied
        attempts = 0
        while attempts < self.passwd_attempts:
            
            passAttempt = self.remClientSocket.recv(self.BufferSize)
            #This block is in a try-except, in the event that the other person exits on password retry
            try:
                #If password match, send Granted response and break loop
                if decrypt(key['private'],passAttempt) == hostPasswordHash:
                    self.remClientSocket.send(bytes("Granted",'utf8'))
                    print(f"S: Password match from {self.remClientAddress[0]}")
                    break
                else:
                    self.remClientSocket.send(bytes("Denied",'utf8'))
                    print(f"S: Password failed attempt from {self.remClientAddress[0]}")
                    attempts += 1
            except:
                print(f"S: {self.remClientAddress[0]} Left during password authentication")
                return

        if attempts == self.passwd_attempts:
            print("S: Password attempts exceeded.")
            return


        #Symmetric Key Exchange

        #Recieve and decode it with local private key
        symmkeyRemote = self.remClientSocket.recv(self.BufferSize)
        symmkeyRemote = decrypt(key['private'],symmkeyRemote)
        symmkeyRemote = Fernet(symmkeyRemote)
        print(f"S: Recieved symmetric key from {self.remClientAddress[0]}")

        
        mode = receiveMsg(socket=self.remClientSocket, BufferSize=self.BufferSize)
        if mode == "RetrievalMode":
            print("S: (retrievalMode): receiving locations to send them and load in memory")
            locations = receiveLocationsList(socket=self.remClientSocket, BufferSize=self.BufferSize)
            self.loadDataFromStorage(locationList=locations)
            if self.payload == None:
                "S: (retrievalMode) Data not found, exiting..."
                self.remClientSocket.close()
                return
            
            "S: (retrievalMode) Sending the Payload"
            self.remClientSocket.send(self.payload)

        elif mode == "StorageMode":
            self.payload = receivePayload(socket=self.remClientSocket)
            print("S: (not RetrievalMode) recieved", self.payload.getbuffer().nbytes)
            locations = []
            print("S: (not RetrievalMode): saving payload and sending locations of stored files")
            for _ in range(self.localRedundancyCount):
                fileName = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10))
                locations.append(f"C://Desktop//{fileName}.bin")
                self.savePayload(f"C://Desktop//{fileName}.bin")

            sendLocationsList(socket=self.remClientSocket, locationList=locations)
        else:
            print("S: unknown mode received: ", mode)

        # self.payload = self.payload.decode('utf8')
        # self.sendSocket.send() TODO: send back loaction of the file
        self.remClientSocket.close()
        print("S: Closing sockets")
        return self.payload
    
    def savePayload(self, location):
        with open("output.txt", "wb") as f:
            self.payload.seek(0)
            f.write(self.payload.getbuffer())
    

    def loadDataFromStorage(self, locationList):
        for path in locationList:
            my_file = pathlib.Path(path)
            if my_file.is_file():
                with open(path, "rb") as f:
                    self.payload = f.read()
                    if(len(self.payload) == CHUNK_SIZE):
                        return
