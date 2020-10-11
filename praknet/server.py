import os
from praknet import handler
from praknet import messages
from praknet import socket
import struct

options = {
    "name": "",
    "ip": "0.0.0.0",
    "port": 19132,
    "server_guid": struct.unpack(">Q", os.urandom(8))[0],
    "custom_handler": lambda data, addr, socket: 0,
    "custom_packets": [0x84]
}

connections = {}

def add_connection(addr, port):
    token = str(addr) + ":" + str(port)
    connections[token] = {}

def remove_connection(addr, port):
    token = str(addr) + ":" + str(port)
    if token in connections:
        del connections[token]

def get_connection(addr, port):
    token = str(addr) + ":" + str(port)
    if token in connections:
        return connections[token]
    else:
        return None

def set_option(option, value):
    options[option] = value

def packet_handler(data, address):
    id = data[0]
    if id == messages.ID_UNCONNECTED_PING:
        socket.send_buffer(handler.handle_unconnected_ping(data), address)
    elif id == messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS:
        socket.send_buffer(handler.handle_unconnected_ping_open_connections(data), address)

def run():
    socket.create_socket((options["ip"], options["port"]))
    while True:
        recv = socket.receive_buffer()
        if recv != None:
            data, addr = recv
            packet_handler(data, addr)
