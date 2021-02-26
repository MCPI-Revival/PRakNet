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

from copy import copy
import os
from praknet import handler
from praknet import packets
import socket
import struct

options = {
    "name": "MCCPP;Demo;Default PRakNet motd",
    "ip": "0.0.0.0",
    "port": 19132,
    "server_guid": struct.unpack(">Q", os.urandom(8))[0],
    "custom_handler": lambda data, addr: 0,
    "accepted_raknet_protocols": [5],
    "debug": False
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
connections = {}

def add_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    connections[token] = {
        "mtu_size": 0,
        "address": address,
        "is_connected": False,
        "sequence_number": 0,
        "received_sequence_number": 0,
        "received_sequence_numbers": [],
        "recovery_queue": {},
        "ack_queue": [],
        "nack_queue": [],
        "queue": {
            "id": 0x80,
            "sequence_number": 0,
            "frames": []
        },
        "fragmented_packets": {},
        "fragment_id": 0
    }

def remove_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    if token in connections:
        body = bytes([packets.connection_closed["id"]])
        packet = copy(packets.frame)
        packet["reliability"] = 0
        packet["body"] = body
        send_frame(packet, address)
        del connections[token]

def get_connection(address):
    token = str(address[0]) + ":" + str(address[1])
    if token in connections:
        return connections[token]
    
def send_queue(address):
    connection = get_connection(address)
    if len(connection["queue"]["frames"]) > 0:
        connection["queue"]["sequence_number"] = connection["sequence_number"]
        connection["sequence_number"] += 1
        connection["recovery_queue"][connection["queue"]["sequence_number"]] = connection["queue"]
        server_socket.sendto(packets.write_frame_set(connection["queue"]), address)
        connection["queue"]["frames"] = []
        
def broadcast_queue():
    for connection in connections.values():
        send_queue(connection["address"])
    
def send_frame(packet, address, is_imediate = True):
    connection = get_connection(address)
    if is_imediate:
        connection["queue"]["frames"].append(packet)
        send_queue(address)
    else:
        frame_length = len(packets.write_frame(packet))
        queue_length = len(packets.write_frame_set(connection["queue"]))
        if queue_length + frame_length >= connection["mtu_size"]:
            send_queue(address)
        connection["queue"]["frames"].append(packet)

def broadcast_frame(packet, is_imediate = True):
    for connection in connections.values():
        send_frame(packet, connection["address"], is_imediate)
        
def send_ack_queue(address):
    connection = get_connection(address)
    packet = copy(packets.ack)
    packet["packets"] = connection["ack_queue"]
    server_socket.sendto(packets.write_acknowledgement(packet), address)
    connection["ack_queue"] = []
    
def send_nack_queue(address):
    connection = get_connection(address)
    packet = copy(packets.nack)
    packet["packets"] = connection["nack_queue"]
    server_socket.sendto(packets.write_acknowledgement(packet), address)
    connection["nack_queue"] = []
    
def broadcast_acknowledgement_queues():
    for connection in connections.values():
        send_ack_queue(connection["address"])
        send_nack_queue(connection["address"])
        
def fragmented_frame_handler(frame, address):
    connection = get_connection(address)
    if frame["fragment"]["id"] not in connection["fragmented_packets"]:
        connection["fragmented_packets"][frame["fragment"]["id"]] = {frame["fragment"]["index"]: frame}
    else:
        connection["fragmented_packets"][frame["fragment"]["id"]][frame["fragment"]["index"]] = frame
    if len(connection["fragmented_packets"][frame["fragment"]["id"]]) == frame["fragment"]["size"]:
        new_frame = copy(packets.frame)
        new_frame["body"] = b""
        for i in range(0, frame["fragment"]["size"]):
            new_frame["body"] += connection["fragmented_packets"][frame["fragment"]["id"]][i]["body"]
        del connection["fragmented_packets"][frame["fragment"]["id"]]
        frame_handler(new_frame)
        
def frame_handler(frame, address):
    connection = get_connection(address)
    if frame["is_fragmented"]:
        fragmented_frame_handler(frame, address)
    else:
        identifier = frame["body"][0]
        if identifier < 0x80:
            if not connection["is_connected"]:
                if identifier == packets.connection_request["id"]:
                    body = handler.handle_connection_request(frame["body"], address)
                    packet = copy(packets.frame)
                    packet["reliability"] = 0
                    packet["body"] = body
                    send_frame(packet, address)
                elif identifier == packets.new_connection["id"]:
                    packet = packets.read_new_connection(frame["body"])
                    connection["is_connected"] = True
            elif identifier == packets.connection_closed["id"]:
                remove_connection(address)
            elif identifier == packets.connected_ping["id"]:
                body = handler.handle_connected_ping(frame["body"])
                packet = copy(packets.frame)
                packet["reliability"] = 0
                packet["body"] = body
                send_frame(packet, address, False)
        elif connection["is_connected"]:
            if options["debug"]:
                print("Received frame -> " + str(hex(identifier)))
            options["custom_handler"](frame, address)
    
def packet_handler(data, address):
    identifier = data[0]
    connection = get_connection(address)
    if connection != None:
        if identifier == packets.nack["id"]:
            packet = packets.read_acknowledgement(data)
            for sequence_number in packet["packets"]:
                if sequence_number in connection["recovery_queue"]:
                    lost_packet = connection["recovery_queue"][sequence_number]
                    lost_packet["sequence_number"] = connection["sequence_number"]
                    connection["sequence_number"] += 1
                    server_socket.sendto(packets.write_frame_set(lost_packet), address)
                    del connection["recovery_queue"][sequence_number]
        elif identifier == packets.ack["id"]:
            packet = packets.read_acknowledgement(data)
            for sequence_number in packet["packets"]:
                if sequence_number in connection["recovery_queue"]:
                    del connection["recovery_queue"][sequence_number]
        elif 0x80 <= identifier <= 0x8f:
            frame_set = packets.read_frame_set(data)
            if frame_set["sequence_number"] in connection["received_sequence_numbers"]:
                return
            connection["received_sequence_numbers"].append(frame_set["sequence_number"])
            connection["ack_queue"].append(frame_set["sequence_number"])
            hole_length = frame_set["sequence_number"] - connection["received_sequence_number"]
            if hole_length > 0:
                for sequence_number in range(connection["received_sequence_number"] + 1, hole_length):
                    if sequence_number not in connection["received_sequence_numbers"]:
                        connection["nack_queue"].append(sequence_number)
            connection["received_sequence_number"] = frame_set["sequence_number"]                  
            for frame in frame_set["frames"]:
                frame_handler(frame, address)
    elif identifier == packets.unconnected_ping["id"]:
        server_socket.sendto(handler.handle_unconnected_ping(data), address)
    elif identifier == packets.unconnected_ping_open_connections["id"]:
        server_socket.sendto(handler.handle_unconnected_ping(data), address)
    elif identifier == packets.open_connection_request_1["id"]:
        server_socket.sendto(handler.handle_open_connection_request_1(data), address)
    elif identifier == packets.open_connection_request_2["id"]:
        server_socket.sendto(handler.handle_open_connection_request_2(data, address), address)

def run():
    try:
        server_socket.bind((options["ip"], options["port"]))
    except socket.error as e:
        raise Exception("Failed to bind!\n" + str(e))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        recv = server_socket.recvfrom(65535)
        if recv != None:
            data, address = recv
            packet_handler(data, address)
        broadcast_acknowledgement_queues()
        broadcast_queue()
