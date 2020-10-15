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
    "custom_handler": lambda data, addr: 0
}

status = {
    "connecting": 0,
    "connected": 1,
    "disconnecting": 2,
    "disconnected": 3
}

connections = {}

def add_connection(addr, port):
    token = str(addr) + ":" + str(port)
    connections[token] = {
        "connection_state": status["connecting"]
    }

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
    connection = get_connection(address[0], address[1])
    if connection != None:
        try:
            if data[4] == 0x00:
                datapacket_id = data[7]
            elif data[4] == 0x40:
                datapacket_id = data[10]
            elif data[4] == 0x60:
                datapacket_id = data[14]
            else:
                datapacket_id = -1
        except:
            datapacket_id = -1
        if datapacket_id < 0x80:
           if datapacket_id == messages.ID_CONNECTION_REQUEST:
               socket.send_buffer(handler.handle_connection_request(data, (address[0], address[1], 4)), address)
    elif id == messages.ID_UNCONNECTED_PING:
        socket.send_buffer(handler.handle_unconnected_ping(data), address)
    elif id == messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS:
        socket.send_buffer(handler.handle_unconnected_ping_open_connections(data), address)
    elif id == messages.ID_OPEN_CONNECTION_REQUEST_1:
        socket.send_buffer(handler.handle_open_connection_request_1(data), address)
    elif id == messages.ID_OPEN_CONNECTION_REQUEST_2:
        socket.send_buffer(handler.handle_open_connection_request_2(data, (address[0], address[1], 4)), address)

def run():
    socket.create_socket((options["ip"], options["port"]))
    while True:
        recv = socket.receive_buffer()
        if recv != None:
            data, addr = recv
            packet_handler(data, addr)
            options["custom_handler"](data, addr)
