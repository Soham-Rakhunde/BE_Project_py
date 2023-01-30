# import socket, ssl, pprint
# context = ssl.create_default_context()
# conn = context.wrap_socket(socket.socket(socket.AF_INET),
#                            server_hostname="www.python.org")
# conn.connect(("www.python.org", 443))
# cert = conn.getpeercert()
# print(cert)
# pprint.pprint(len(context.get_ca_certs(binary_form=False)))


# # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # # require a certificate from the server
# # ssl_sock = ssl.wrap_socket(s,
# #                            ca_certs="/etc/ca_certs_file",
# #                            cert_reqs=ssl.CERT_REQUIRED)
# # ssl_sock.connect(('www.verisign.com', 443))

# # pprint.pprint(ssl_sock.getpeercert())
# # # note that closing the SSLSocket will also close the underlying socket
# # ssl_sock.close()
# # # class TracerService:

import socket, ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="ca.crt", keyfile="ca.pem")
# SSLContext.load_verify_locations()
bindsocket = socket.socket()
bindsocket.bind(('127.0.0.1', 10023))
bindsocket.listen(5)

def handle_client(clientsocket, client_address):
    print(f"Accepted connection from {client_address}")
    secure_socket = context.wrap_socket(clientsocket, server_side=True)

    data = secure_socket.recv(1024)
    secure_socket.send(b'ACK: ' + data)

print("SSSS")
while True:
    (clientsocket, client_address) = bindsocket.accept()
    handle_client(clientsocket, client_address)