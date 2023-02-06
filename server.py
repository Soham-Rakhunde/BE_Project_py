from services.network_services.receiverTLSInterface import TLSReceiver
import concurrent.futures

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futs = []
        for i in range(1,4):
            print("START", i)
            ob = TLSReceiver(threadPoolExecutor = executor, remoteAddress = '192.168.0.105', localPort= 11110+i)
            # res = executor.map(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd',remoteaddress='192.168.0.105')
            # fut = executor.submit(ob.connectToRemoteClient,keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd',remoteaddress='192.168.0.105')
            ob.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd',remoteaddress='192.168.0.105')
        
            # futs.append(fut)
            print("LOOP", i)


        # concurrent.futures.wait(futs)
            # print(res.result())
        # for f in concurrent.futures.as_completed(futs):
        #     print(f)