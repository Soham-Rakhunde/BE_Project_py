#################################################################################################################################################################
# References
#   Generating self-signed certificate     https://cryptography.io/en/latest/x509/tutorial/
#   RSA Cryptography                       https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
#   TLS/SSL secured socket                 https://docs.python.org/3/library/ssl.html
#   Multithreading                         https://realpython.com/intro-to-python-threading/


# Items necessary to perform operations with private/public keys
from concurrent.futures import ThreadPoolExecutor
import pathlib
import platform
import secrets
import string
from subprocess import check_output
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from services.hiding_service.image_gatherer import ImageGatherer
from services.hiding_service.steganography_module import StegDecoder, StegEncoder
from ui.printer import Printer
from utils.constants import CHUNK_SIZE, TLS_MAX_SIZE
from utils.socket_util_functions import receiveLocationsList, receiveMsg, receivePayload, sendLocationsList
from utils.tls_util_functions import *
import gradio as gr


# Python server/client module, as well as ssl module to wrap the socket in TLS
import socket
import ssl

# Detecting whether the script is running in Windows or otherwise by importing the msvcrt module
# try:
#     import msvcrt
#     win = 1
# except:
#     win = 0

# Multithreading for simultaneously sending and recieving messages
import threading


class PeerTLSInterface:
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
    localRedundancyCount = 2
    locationsList: list = None

    threadPoolExecutor: ThreadPoolExecutor = None
    payload: bytes = None

    # as we maintrain remote clients socket as interface
    remClientSocket: ssl.SSLSocket = None

    hashingAlgorithm = hashes.SHA512()
    passwd_hashingAlgorithm = hashes.SHA256()
    passwd_attempts = 4
    BufferSize = 1024
    progress = None
    mode = "Not decided yet"

    # UI functions

    def progress_update(self, percent, desc):
        if self.progress != None:
            self.progress(percent/100, desc=desc, unit="percent")

    def progress_tqdm(self, iter, desc):
        if self.progress != None:
            return self.progress.tqdm(iter, desc=desc, unit="percent")
        else:
            return iter

    def __init__(
        self,
        remoteAddress: str,
        localPort: int,
        retrievalMode: bool = False,
        threadPoolExecutor: ThreadPoolExecutor = None,
        locationsList: list = None,
        progress: gr.Progress = None
    ):
        self.remClientAddress = remoteAddress
        self.threadPoolExecutor = threadPoolExecutor
        self.localPort = localPort
        self.retrievalMode = retrievalMode
        self.locationsList = locationsList
        self.progress = progress

        if platform.uname().system == 'Windows':
            hostname = socket.gethostname()
            self.localServerAddress = socket.gethostbyname(hostname)
        else:
            self.localServerAddress = str(check_output(
                ['hostname', '--all-ip-addresses']))[2:-4]
        # self.updateUIValues()

        self.printer = Printer()

        # Create directories to house the host identity, and remote public certs
        if not os.path.isdir('Identity'):
            os.mkdir('Identity')
        if not os.path.isdir('RemoteCerts'):
            os.mkdir('RemoteCerts')
        # Check that the port number is above 1000, and that all other inputs have something there before proceeding
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

    def connectToRemoteClient(self, networkPassword, localRedundancyCount):
        # Generate self-signed certificate if it doesn't exist
        makeCert()

        self.localRedundancyCount = localRedundancyCount
        keyHandler = KeyHandlerUI()
        keypasswd = keyHandler.key
        print(keypasswd)
        # TLS client socket object
        serverContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        serverContext.load_cert_chain(
            'Identity/certificate.pem', 'Identity/private_key.pem', password=keypasswd)

        serverSocketI = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        serverSocket = serverContext.wrap_socket(
            serverSocketI, server_side=True)

        # Bind the server socket to localhost, and turn off timeout so it can listen forever
        try:
            # serverSocket.bind(('0.0.0.0', 0))
            # serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # self.localPort = serverSocket.getsockname()[1]
            serverSocket.bind(('0.0.0.0', self.localPort))
        except OSError:
            print(
                "S: Likely serverPort already in use (Linux has a brief timeout between runs)")
            self.printer.write(
                name='S', msg='Likely serverPort already in use (Linux has a brief timeout between runs)')
            return
        serverSocket.settimeout(None)

        # The socket accept operation has doesn't seem to have a means of exiting once it's started. So I worked around this by
        # having this function running in a separate thread, which makes a connection to localhost
        def exitCatchTM(localPort, timeout):
            # Hold here until timeout criteria is reached, then close the connection
            x = datetime.datetime.utcnow().timestamp()
            while (not ((datetime.datetime.utcnow().timestamp() - x) > timeout)) or not timeout:
                pass

            if serverSocket == None:
                print("Exiting Catch timeout", serverSocket)
                dummysocket = socket.create_connection(
                    ('127.0.0.1', localPort))
                clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
                dummySocketS = clientContext.wrap_socket(
                    dummysocket, server_hostname='127.0.0.1')

        def exitCatchKP(localPort):
            input()
            print("Exiting Catch KP", serverSocket)
            if serverSocket == None:
                dummysocket = socket.create_connection(
                    ('127.0.0.1', localPort))
                clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS)
                dummySocketS = clientContext.wrap_socket(
                    dummysocket, server_hostname='127.0.0.1')

        quitK = threading.Thread(
            target=exitCatchKP, args=(self.localPort,), daemon=True)
        quitK.start()
        quitT = threading.Thread(target=exitCatchTM, args=(
            self.localPort, self.timeout,), daemon=True)
        quitT.start()

        print(
            f"S: Listening on LocalServerPort {self.localPort} (Press Enter to exit)...")
        self.printer.write(
            name='S', msg=f"Listening on LocalServerPort {self.localPort} (Press Enter to exit)...")
        self.progress_update(5, desc='Sockets listening')

        # Start listening for connection
        serverSocket.listen(1)
        remoteAddress = self.remClientAddress
        try:
            self.remClientSocket, self.remClientAddress = serverSocket.accept()
        except ConnectionAbortedError:
            print("S: Connection Cancelled, or timed out")
            self.printer.write(
                name='S', msg="Connection Cancelled, or timed out")
            return
        print("S: Connected to client address:", self.remClientAddress)
        self.printer.write(
            name='S', msg=f"Connected to client address: {self.remClientAddress}")
        # If the remote connection was localhost (operation cancelled), exit the script
        if self.remClientAddress[0] == '127.0.0.1':
            serverSocket.close()
            print("S: Connection Cancelled, or timed out")
            self.printer.write(
                name='S', msg=f"Connection Cancelled, or timed out")
            return
        # if self.remClientAddress[0] != remoteAddress:
        #     serverSocket.close()
        #     print(f"S: Connection recieved from unexpected host ({self.remClientAddress[0]})")
        #     self.printer.write(name='S', msg=f"Connection recieved from unexpected host ({self.remClientAddress[0]})")
        #     return

        print(f"S: Established connection from {self.remClientAddress[0]}")
        self.printer.write(
            name='S', msg=f"Established connection from {self.remClientAddress[0]}")

        self.progress_update(
            7, desc=f'Connection established with {self.remClientAddress[0]}')

    #     self.payloadFuture = self.threadPoolExecutor.submit(self.authenticateAndReveive, networkPassword, keypasswd)
    # commentng for testing receive functionality
    # def authenticateAndReveive(self, networkPassword, keypasswd):
        # print("S: Thread Spawned")
        # Generate keypair for password exchange
        # key = makeKey()
        key = retrieveKey()
        print("S: Retrieved Keypair")
        self.printer.write(name='S', msg=f"Retrieved Keypair")

        self.progress_update(10, desc=f'Retrieveied keypair')

        # Hash the passwords before sending them over the wire
        h = hashes.Hash(self.passwd_hashingAlgorithm,
                        backend=default_backend())
        h.update(bytes(networkPassword, 'utf8'))
        hostPasswordHash = h.finalize()
        # h = hashes.Hash(self.passwd_hashingAlgorithm,backend=default_backend())
        # h.update(bytes(remotepassword,'utf8'))
        # remotepassword = h.finalize()

        # Send the other node the public key, then wait for password attempt
        self.remClientSocket.send(pubString(key['public']))
        print(f"S: Sent public key to {self.remClientAddress[0]}")
        self.printer.write(
            name='S', msg=f"Sent public key to {self.remClientAddress[0]}")

        # If the password matches, send a Granted message. Else send denied
        attempts = 0
        while attempts < self.passwd_attempts:

            passAttempt = self.remClientSocket.recv(self.BufferSize)
            # This block is in a try-except, in the event that the other person exits on password retry
            try:
                # If password match, send Granted response and break loop
                if decrypt(key['private'], passAttempt) == hostPasswordHash:
                    self.remClientSocket.send(bytes("Granted", 'utf8'))
                    print(f"S: Password match from {self.remClientAddress[0]}")
                    self.printer.write(
                        name='S', msg=f"Password match from {self.remClientAddress[0]}")
                    break
                else:
                    self.remClientSocket.send(bytes("Denied", 'utf8'))
                    print(
                        f"S: Password failed attempt from {self.remClientAddress[0]}")
                    self.printer.write(
                        name='S', msg=f"Password failed attempt from {self.remClientAddress[0]}")
                    attempts += 1
            except:
                print(
                    f"S: {self.remClientAddress[0]} Left during password authentication")
                self.printer.write(
                    name='S', msg=f"{self.remClientAddress[0]} Left during password authentication")
                return

        if attempts == self.passwd_attempts:
            print("S: Password attempts exceeded.")
            self.printer.write(name='S', msg=f"Password attempts exceeded.")
            return

        self.progress_update(23, desc=f'Password verification completed')

        # Symmetric Key Exchange

        # Recieve and decode it with local private key
        # symmkeyRemote = self.remClientSocket.recv(self.BufferSize)
        # symmkeyRemote = decrypt(key['private'], symmkeyRemote)
        # symmkeyRemote = Fernet(symmkeyRemote)
        # print(f"S: Recieved and decrypted symmetric key from {self.remClientAddress[0]}")
        # self.printer.write(
        #     name='S', msg=f"Recieved and decrypted 128 bit symmetric session key from {self.remClientAddress[0]}")

        # self.progress_update(30, desc=f'Key exchange completed successfully')

        self.mode = receiveMsg(socket=self.remClientSocket,
                               BufferSize=self.BufferSize)

        # self.updateUIValues()
        self.progress_update(30, desc='Received mode message successfully')
        if self.mode == "RetrievalMode":
            print(
                "S: (retrievalMode): receiving locations to send them and load in memory")
            self.printer.write(
                name='S(retrievalMode)', msg=f"Receiving locations to send them and load in memory")
            self.locationsList = receiveLocationsList(
                socket=self.remClientSocket, BufferSize=self.BufferSize)
            self.progress_update(45, desc='Received locations')

            locationIndex = 0

            # If HMAC is incorrect then they can retry
            while locationIndex < len(self.locationsList):
                self.loadDataFromStorage(
                    searchFromIndex=locationIndex, locationList=self.locationsList)
                # self.updateUIValues()
                if self.payload == None:
                    "S: (retrievalMode) Data not found, exiting..."
                    self.printer.write(name='S(retrievalMode)',
                                       msg=f"Data not found, exiting...")
                    self.remClientSocket.close()
                    return

                "S: (retrievalMode) Sending the Payload"

                self.progress_update(65, desc='Sending data')
                self.printer.write(name='S(retrievalMode)',
                                   msg=f"Sending the Payload")
                self.remClientSocket.send(self.payload)
                msg = receiveMsg(socket=self.remClientSocket,
                                 BufferSize=self.BufferSize)
                if msg == "END":
                    self.progress_update(100, desc='Completed')
                    break
                else:
                    locationIndex = max(locationIndex, int(msg))

        elif self.mode == "StorageMode":
            self.progress_update(40, desc='Receiving data for storage')
            self.payload = receivePayload(socket=self.remClientSocket)
            print("S: (not RetrievalMode) recieved",
                  self.payload.getbuffer().nbytes)
            self.printer.write(
                name='S(storeMode)', msg=f"recieved {self.payload.getbuffer().nbytes} bytes")
            self.progress_update(70, desc='Received data successfully')
            self.locationsList = []

            # if platform.uname().system == 'Windows':
            #     path = os.path.join(os.path.join(
            #         os.environ['USERPROFILE']), 'Desktop')
            # else:
            #     path = os.path.join(os.path.join(
            #         os.path.expanduser('~')), 'Desktop')
            print(
                f"S: (not RetrievalMode): hiding payload in images and sending locations of stored files")
            self.printer.write(
                name='S(storeMode)', msg=f"hiding payload in images and sending locations of stored files")
            self.progress_update(80, desc='Saving data locally')

            self.savePayloadSteg()

            # for _ in self.progress_tqdm(range(self.localRedundancyCount), f"Saving {self.localRedundancyCount} times for redundancy"):
            # fileName = ''.join(secrets.choice(
            #     string.ascii_uppercase + string.digits) for i in range(10))

            # self.updateUIValues()
            self.progress_update(
                95, desc='Sending locations list back to sender')
            sendLocationsList(socket=self.remClientSocket,
                              locationList=self.locationsList)
        else:
            print("S: unknown mode received: ", self.mode)
            self.printer.write(
                name='S', msg=f"unknown mode received: {self.mode}")
            self.remClientSocket.close()
            return

        print("S: Transaction complete, Ending connection")
        self.printer.write(
            name='S', msg=f"Transaction complete, Ending connection")
        self.remClientSocket.close()
        self.progress_update(100, desc='Completed successfully')

        return self.payload

    def createNewPathforSteg(self, orig_img_path):
        orig_img_path = str(orig_img_path)
        l = orig_img_path.split('.')
        l[-2] += str(uuid.uuid4())
        while True:
            steg_img_path = '.'.join(l)
            if not os.path.exists(steg_img_path):
                return steg_img_path

    def savePayloadSteg(self):
        imgLocator = ImageGatherer()
        pathsItr = imgLocator.nextPathIterator(size=self.localRedundancyCount)

        for copy_num in self.progress_tqdm(range(self.localRedundancyCount), f"Saving {self.localRedundancyCount} times for redundancy"):
            imgPath = next(pathsItr)
            stegPath = self.createNewPathforSteg(orig_img_path=imgPath)
            try:
                stegEncoder = StegEncoder(
                    input_image=imgPath, message=self.payload.getbuffer())
                secret = stegEncoder.encode()
                secret.save(stegPath)
                print(
                    f"Steganography: Succesfully hidden payload in image at {stegPath}, for the redundant copy number {copy_num}")
                self.printer.write(
                    name='Steganography', msg=f"Succesfully hidden payload in image at {stegPath}, for the redundant copy number {copy_num}")
            except:
                copy_num -= 1  # unsuccessful attempt
                print(
                    f"Steganography: Redundant copy hiding unsuccessful attempt, Retrying...")
                self.printer.write(
                    name='Steganography', msg=f"Redundant copy hiding unsuccessful attempt, Retrying...")

                pass
            self.locationsList.append(stegPath)

    def retrieveStoredPayloadSteg(self, steg_img_path):
        try:
            stegDecoder = StegDecoder(encoded_image=steg_img_path)
            payload = stegDecoder.decode()
            print(
                f"Steganography: Succesfully decoded and retrieved payload from image at {steg_img_path}")
            self.printer.write(
                name='Steganography', msg=f"Steganography: Succesfully decoded and retrieved payload from image at {steg_img_path}")
        except:
            copy_num -= 1  # unsuccessful attempt
            print(
                f"Steganography: Could not retrieve the data from steganographed image")
            self.printer.write(
                name='Steganography', msg=f"Could not retrieve the data from steganographed image")
            payload

        return payload

    def loadDataFromStorage(self, searchFromIndex, locationList):
        print("LocationList:", locationList)
        self.printer.write(name='LocationList', msg=f"{locationList}")
        for path in self.progress_tqdm(locationList[searchFromIndex:], "Finding files from location list"):
            my_file = pathlib.Path(path)
            if my_file.is_file():
                self.payload = self.retrieveStoredPayloadSteg(
                    steg_img_path=path)
                if (len(self.payload) == CHUNK_SIZE):
                    print(f"S: data found at {path}")
                    self.printer.write(
                        name='S', msg=f"data found at {path}")
                    return
                else:
                    print(f"S: data at {path} is corrupted, retrying...")
                    self.printer.write(
                        name='S', msg=f"data at {path} is corrupted, retrying...")
