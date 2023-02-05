
from services.network_services.receiverTLSInterface import TLSReceiver


ob = TLSReceiver(multiProcessExecutor = None, remoteAddress = '192.168.0.105', localPort= 11111)
ob.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd',remoteaddress='192.168.0.105')