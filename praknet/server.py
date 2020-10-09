from praknet import handler
from praknet import messages
from praknet import socket

options = {
    "name": "",
    "port": 0,
    "custom_handler": lambda data, addr, socket: 0,
    "custom_packets": [0x84]
}

def packet_handler(data, address):
    if data[0] == messages.ID_UNCONNECTED_PING:
        socket.sendBuffer(handler.handle_unconnected_ping(data), address)

def run():
    socket.create_socket(19132)
    while True:
        recv = socket.receive_buffer()
        if recv != None:
            packet_handler(recv[0], recv[1])
