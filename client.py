import concurrent.futures
from services.network_services.senderTLSInterface import TLSender

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futs = []
        for i in range(1,5):
            print("START", i)
            ob = TLSender(payload= f"HIII {i}", threadPoolExecutor = executor, remoteAddress = '192.168.0.105', remotePort =11110+i)
            # res = executor.map(ob.connectToRemoteServer, remotepassword='P@ssw0rd')
            ob.connectToRemoteServer(remotepassword='P@ssw0rd')
            # futs.append(ob.connectToRemoteServer(remotepassword='P@ssw0rd'))
            print("LOOP", i)

        # concurrent.futures.wait(futs)
        # for f in concurrent.futures.as_completed(futs):
        #     print(f)