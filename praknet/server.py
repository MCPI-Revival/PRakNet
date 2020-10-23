import os
from praknet import handler
from praknet import messages
from praknet import packets
from praknet import socket
import struct

options = {
    "name": "",
    "ip": "0.0.0.0",
    "port": 19132,
    "server_guid": struct.unpack(">Q", os.urandom(8))[0],
    "custom_handler": lambda data, addr: 0,
    "accepted_raknet_protocols": [5, 6, 7, 8, 9, 10]
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
        "connecton_state": status["connecting"],
        "packets_queue": [],
        "iteration": 0
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

def add_to_queue(data, address):
    connection = get_connection(address[0], address[1])
    connection["packets_queue"].append(data)
    if connection["iteration"] >= 255:
        connection["iteration"] = 0
    else:
        connection["iteration"] += 1

def get_last_packet(address):
    connection = get_connection(address[0], address[1])
    queue = connection["packets_queue"]
    if len(queue) > 0:
        return queue[-1]
    else:
        return b""

def packet_handler(data, address):
    id = data[0]
    connection = get_connection(address[0], address[1])
    if connection != None:
        if id == messages.ID_ACK:
            packets.read_encapsulated(get_last_packet(address))
            if not packets.encapsulated["is_invalid"]:
                packets.encapsulated["iteration"] = connection["iteration"]
                packets.encapsulated["encapsulation"] = 0x00
            socket.send_buffer(packets.write_encapsulated(), address)
        else:
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
            if datapacket_id != -1:
                if datapacket_id != messages.ID_CONNECTED_PING:
                    connection = get_connection(address[0], address[1])
                    buffer = b""
                    buffer += b"\xc0\x00\x01\x01"
                    buffer += bytes([connection["iteration"]])
                    buffer += b"\x00\x00"
                    socket.send_buffer(buffer, address)
                if connection["connecton_state"] == status["connecting"]:
                    if datapacket_id == messages.ID_CONNECTION_REQUEST:
                        buffer = handler.handle_connection_request(data, (address[0], address[1], 4))
                        socket.send_buffer(buffer, address)
                        add_to_queue(buffer, address)
                    elif datapacket_id == messages.ID_NEW_CONNECTION:
                        packets.read_encapsulated(data)
                        packets.read_connected_ping(packets.encapsulated["data_packet"])
                        connection = get_connection(address[0], address[1])
                        connection["connecton_state"] = status["connected"]
                if connection["connecton_state"] == status["connected"]:
                    if datapacket_id == messages.ID_CONNECTED_PING:
                        buffer = handler.handle_connected_ping(data, address)
                        socket.send_buffer(buffer, address)
                        add_to_queue(buffer, address)
                    elif datapacket_id == messages.ID_CONNECTION_CLOSED:
                        connection["connecton_state"] = status["disconnecting"]
                        remove_connection(address[0], address[1])
                        connection["connecton_state"] = status["disconnected"]
                    options["custom_handler"](data, address)
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
