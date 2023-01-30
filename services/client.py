import ssl
import socket

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
# context.load_verify_locations('ca.crt')
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(clientsocket, server_hostname="localhost")
secure_socket.connect(("localhost", 10023))

secure_socket.send(b"Hello from the client")
data = secure_socket.recv(1024)
print("Received: ", data.decode())

secure_socket.close()
