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
from praknet import packets
import socket
import struct
import time

options = {
    "ip": "0.0.0.0",
    "port": 19132,
    "guid": struct.unpack(">Q", os.urandom(8))[0],
    "protocol_version": 5,
    "debug": False,
    "custom_handler": lambda frame: 0,
    "magic": b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78",
    "mtu_size": 512
}

# State 0: Offline
# State 1: Connecting
# State 2: Connected

connection = {
    "sequence_number": 0,
    "reliable_index": 0,
    "sent_packets": [],
    "state": 0
}

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def send_packet(data):
    client_socket.sendto(data, (options["ip"], options["port"]))

def send_frame(packet):
    new_packet = copy(packets.frame_set)
    new_packet["sequence_number"] = connection["sequence_number"]
    new_packet["frame"] = packet
    send_packet(packets.write_frame_set(new_packet))
    connection["sent_packets"].append(packet)
    connection["sequence_number"] += 1
    
def send_reliable(data):
    packet = copy(packets.frame)
    packet["reliability"] = 2
    packet["reliable_index"] = connection["reliable_index"]
    connection["reliable_index"] += 1
    packet["body"] = data
    send_frame(packet)
    
def send_open_connection_request_1():
    packet = copy(packets.open_connection_request_1)
    packet["magic"] = options["magic"]
    packet["protocol_version"] = options["protocol_version"]
    packet["mtu_size"] = options["mtu_size"]
    send_packet(packets.write_open_connection_request_1(packet))
    
def send_open_connection_request_2():
    packet = copy(packets.open_connection_request_2)
    packet["magic"] = options["magic"]
    packet["server_address"] = (options["ip"], options["port"])
    packet["mtu_size"] = options["mtu_size"]
    packet["client_guid"] = options["guid"]
    send_packet(packets.write_open_connection_request_2(packet))
    
def send_connection_request():
    packet = copy(packets.connection_request)
    packet["client_guid"] = options["guid"]
    packet["request_time"] = int(time.time())
    packet["use_security"] = 0
    send_reliable(packets.write_connection_request(packet))
    
def send_new_connection(ping_time):
    packet = copy(packets.new_connection)
    packet["address"] = (options["ip"], options["port"])
    packet["system_addresses"] = [("255.255.255.0", 19132)] * 10
    packet["ping_time"] = int(ping_time)
    packet["pong_time"] = int(time.time())
    send_reliable(packets.write_new_connection(packet))
    connection["state"] = 2
    
def send_connected_ping():
    packet = copy(packets.connected_ping)
    packet["time"] = int(time.time())
    send_reliable(packets.write_connected_ping(packet))
    
def send_connection_closed():
    send_reliable(bytes([packets.connection_closed["id"]]))
    connection["state"] == 0

def send_ack(sequance_numbers):
    packet = copy(packets.ack)
    packet["packets"] = sequence_numbers
    send_packet(packets.write_acknowledgement(packet))

def connect():
    connection["state"] = 1
    while True:
        if connection["state"] == 1:
            step = 0
            if step == 0:
                send_open_connection_request_1()
                recv = client_socket.recvfrom(65535)
                if recv[0][0] == packets.open_connection_reply_1["id"]:
                    step += 1
            elif step == 1:
                send_open_connection_request_2()
                recv = client_socket.recvfrom(65535)
                if recv[0][0] == packets.open_connection_reply_2["id"]:
                    step += 1
            elif step == 2:
                send_connection_request()
                recv = client_socket.recvfrom(65535)
                if 0x80 <= recv[0][0] <= 0x8f:
                    frame_set = packets.read_frame_set(recv[0])
                    if frame_set["frame"]["body"][0] == packets.connection_request_accepted["id"]:
                        send_ack([frame_set["sequence_number"]])
                        packet = packets.read_connection_request_accepted(frame_set["frame"]["body"])
                        send_new_connection(packet["time"])
                        step += 1
        elif connection["state"] == 2:
            recv = client_socket.recvfrom(65535)
            if 0x80 <= recv[0][0] <= 0x8f:
                frame_set = packets.read_frame_set(recv[0])
                send_ack([frame_set["sequence_number"]])
                if frame_set["frame"]["body"][0] == packets.connection_closed["id"]:
                    connection["state"] = 0
                elif frame_set["frame"]["body"][0] == packets.connected_pong["id"]:
                    pass
                else:
                    options["custom_handler"](frame_set["frame"])
                send_connected_ping()
