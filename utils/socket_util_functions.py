import io
import pickle

from utils.constants import *


def sendMsg(socket, msg):
    socket.send(bytes(msg, 'utf-8'))

def receiveMsg(socket, BufferSize):
    msg = socket.recv(BufferSize)
    return msg.decode('utf8')


def receivePayload(socket):
    payload = io.BytesIO()
    for _ in range(int(CHUNK_SIZE/TLS_MAX_SIZE)):
        payload.write(socket.recv(TLS_MAX_SIZE))
    return payload


def sendLocationsList(socket, locationList):
    socket.send(pickle.dumps(locationList))

def receiveLocationsList(socket, BufferSize):
    locations = socket.recv(BufferSize)
    return pickle.loads(locations)
