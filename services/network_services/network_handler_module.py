# from services.network_services.doubleTLS import *
# from utils.singleton_meta import SingletonMeta

# import datetime         #Datetime for chat output
# import threading        #To simultaneously send information with c['localS'], and recieve information with c['remoteS']  

# r_text = list()     #used to share incoming messages between the chat listener thread, and the tkinter main loop for the chat (tkinter isn't very compatible with multithreading)
# BufferSize = 1024


# class NetworkHandler:
#     sendSocket,recieveSocket,symmkeyLocal,symmkeyRemote = [None]*4

#     def __init__(self) -> None:
#         params = {
#             'remoteaddress' :'192.168.106.75',       #127.0.0.1 is used as an exit case in the script. So to connect to localhost, be sure to use your PC's LAN IP address
#             'port'          : 11111,             #Port for the script to listen/connect on
#             'hostpassword'  : 'P@ssw0rd',       #Password that someone connecting to your device will be required to enter when connecting
#             'remotepassword': 'P@ssw0rd',       #Password to submit to the remote host to authenticate the connection
#             'keypassword'   : 'G00dP@ssw0rd',   #Password to unlock your certificate's private key (on first run, you'll be prompted for this when it's being created)
#             'timeout'       : 0                 #Connection timeout value as an integer value in seconds. (0 to listen forever)
#         }

#         s = connect(params)
#         if s:
#             self.sendSocket,self.recieveSocket,self.symmkeyLocal,self.symmkeyRemote = s['localS'],s['remoteS'],s['localK'],s['remoteK']
        
#         #Start listener function for recieved messages
#         listener = threading.Thread(target=self.chatlistener,args=(self.symmkeyLocal,self.recieveSocket,), daemon=True)
#         listener.start()
#         #Main loop
#         rLen = len(r_text)
#         while True:
#             self.sendMessage()
#             if rLen < len(r_text):
#                 rLen = len(r_text)
#                 self.getMessage(r_text[-1])
#         self.sendSocket.close()
#         self.recieveSocket.close()



#     def sendMessage(self):
#         msg = input("input:")
#         #Send message to remote host
#         self.sendSocket.send(self.symmkeyRemote.encrypt(bytes(msg,'utf-8')))
#         print("sending: ",msg)

#     def getMessage(self, msg):
#         print("Received: ",msg)

#     def chatlistener(self, symmkeyLocal,recieveSocket):
#         try:
#             print("listening")
#             while True:
#                 #Recieve message from remote host
#                 message = recieveSocket.recv(BufferSize)
#                 message = symmkeyLocal.decrypt(message)
#                 message = message.decode('utf8')

#                 #Write message to console
#                 r_text.append(message)

#         except ConnectionResetError:
#             print("Chat partner has disconnected")
#         except:
#             pass
       