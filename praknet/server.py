################################################################################
#                                                                              #
#  __  __ _____ ____   ____                 _                                  #
# |  \/  |  ___|  _ \ / ___| __ _ _ __ ___ (_)_ __   __ _                      #
# | |\/| | |_  | | | | |  _ / _` | '_ ` _ \| | '_ \ / _` |                     #
# | |  | |  _| | |_| | |_| | (_| | | | | | | | | | | (_| |                     #
# |_|  |_|_|   |____/ \____|\__,_|_| |_| |_|_|_| |_|\__, |                     #
#                                                    |___/                     #
# Copyright 2021 MFDGaming                                                     #
#                                                                              #
# Permission is hereby granted, free of charge, to any person                  #
# obtaining a copy of this software and associated documentation               #
# files (the "Software"), to deal in the Software without restriction,         #
# including without limitation the rights to use, copy, modify, merge,         #
# publish, distribute, sublicense, and/or sell copies of the Software,         #
# and to permit persons to whom the Software is furnished to do so,            #
# subject to the following conditions:                                         #
#                                                                              #
# The above copyright notice and this permission notice shall be included      #
# in all copies or substantial portions of the Software.                       #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
#                                                                              #
################################################################################

import os
from praknet import handler
from praknet import packets
from praknet import socket
import struct

options = {
    "name": "MCCPP;Demo;Default PRakNet motd",
    "ip": "0.0.0.0",
    "port": 19132,
    "server_guid": struct.unpack(">Q", os.urandom(8))[0],
    "custom_handler": lambda data, addr: 0,
    "accepted_raknet_protocols": [5]
}

connections = {}

def add_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    connections[token] = {
        "mtu_size": 0,
        "address": address,
        "is_connected": False,
        "received_packets": [],
        "sequence_number": 0
    }

def remove_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    if token in connections:
        del connections[token]

def get_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    if token in connections:
        return connections[token]

def set_option(option, value):
    options[option] = value

def receive_packet(data, address):
    connection = get_connection(address[0], address[1])
    connection["received_packets"].append(data)
    if connection["sequence_number"] >= 16777216:
        connection["received_packets"] = []
        connection["sequence_number"] = 0
    else:
        connection["sequence_number"] += 1

def get_last_packet(address):
    connection = get_connection(address[0], address[1])
    queue = connection["received_packets"]
    if len(queue) > 0:
        return queue[-1]
    else:
        return b""
    
def send_ack_queue(address):
    connection = get_connection(address)
    new_packet = copy(packets.ack)
    new_packet["packets"].append(connection["sequence_number"])
    socket.send_buffer(packets.write_acknowledgement(new_packet), address)
    
def send_encapsulated(data, address, reliability, reliable_frame_index = 0, sequenced_frame_index = 0, ordered_frame_index = 0, order_channel = 0, compound_size = 0, compound_id = 0, compound_index = 0):
    connection = get_connection(address[0], address[1])
    packets.encapsulated["body"] = data
    packets.encapsulated["flags"] = reliability
    packets.encapsulated["sequence_order"] = connection["sequence_order"]
    packets.encapsulated["reliable_frame_index"] = reliable_frame_index
    packets.encapsulated["sequenced_frame_index"] = sequenced_frame_index
    packets.encapsulated["order"]["ordered_frame_index"] = ordered_frame_index
    packets.encapsulated["order"]["order_channel"] = order_channel
    packets.encapsulated["fragment"]["compound_size"] = compound_size
    packets.encapsulated["fragment"]["compound_id"] = compound_id
    packets.encapsulated["fragment"]["index"] = compound_index
    packet = packets.write_encapsulated()
    socket.send_buffer(packet, address)
    send_ack_queue(address)
    add_to_queue(packet, address)

def broadcast_encapsulated(data, reliability, reliable_frame_index = 0, sequenced_frame_index = 0, ordered_frame_index = 0, order_channel = 0, compound_size = 0, compound_id = 0, compound_index = 0):
    for connection in connections.values():
        send_encapsulated(data, (connection["address"][0], connection["address"][1]), reliability, reliable_frame_index = 0, sequenced_frame_index = 0, ordered_frame_index = 0, order_channel = 0, compound_size = 0, compound_id = 0, compound_index = 0)
    
def packet_handler(data, address):
    id = data[0]
    connection = get_connection(address[0], address[1])
    if connection != None:
        if id == messages.ID_NACK:
            packets.read_encapsulated(get_last_packet(address))
            packets.encapsulated["flags"] = 0
            packets.encapsulated["sequence_order"] = connection["sequence_order"]
            socket.send_buffer(packets.write_encapsulated(), address)
        elif id == messages.ID_ACK:
            pass
        else:
            send_ack_queue(address)
            packets.read_encapsulated(data)
            data_packet = packets.encapsulated["body"]
            id = data_packet[0]
            print("DATA_PACKET -> " + str(hex(id)))
            if id < 0x80:
                if connection["connecton_state"] == status["connecting"]:
                    if id == messages.ID_CONNECTION_REQUEST:
                        buffer = handler.handle_connection_request(data_packet, connection)
                        send_encapsulated(buffer, address, 0)
                    elif id == messages.ID_NEW_CONNECTION:
                        packets.read_encapsulated(data)
                        packets.read_new_connection(packets.encapsulated["body"])
                        print(packets.new_connection)
                        connection["connecton_state"] = status["connected"]
                elif id == messages.ID_CONNECTION_CLOSED:
                    connection["connecton_state"] = status["disconnecting"]
                    remove_connection(address[0], address[1])
                    connection["connecton_state"] = status["disconnected"]
                elif id == messages.ID_CONNECTED_PING:
                    buffer = handler.handle_connected_ping(data_packet)
                    send_encapsulated(buffer, address, 0)
            if connection["connecton_state"] == status["connected"]:
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
