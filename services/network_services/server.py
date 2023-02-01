import socket, ssl, pprint

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="ca.crt", keyfile="ca.pem", password='password')
# SSLContext.load_verify_locations()
bindsocket = socket.socket()
bindsocket.bind(('127.0.0.1', 10023))
bindsocket.listen(5)

def handle_client(clientsocket, client_address):
    print(f"Accepted connection from {client_address}")
    secure_socket = context.wrap_socket(clientsocket, server_side=True)

    data = secure_socket.recv(1024)
    secure_socket.send(b'ACK: ' + data)



print("Started")
while True:
    (clientsocket, client_address) = bindsocket.accept()
    handle_client(clientsocket, client_address)