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

def send_frame(packet):
    new_packet = copy(packets.frame_set)
    new_packet["sequence_number"] = connection["sequence_number"]
    new_packet["frame"] = packet
    client_socket.sendto(packets.write_frame_set(new_packet), (options["ip"], options["port"]))
    connection["sent_packets"].append(packet)
    connection["sequence_number"] += 1

def connect():
    connection["state"] = 1
    step = 0
    while True:
        if step == 0:
            new_packet = copy(packets.open_connection_request_1)
            new_packet["magic"] = options["magic"]
            new_packet["protocol_version"] = options["protocol_version"]
            new_packet["mtu_size"] = options["mtu_size"]
            client_socket.sendto(packets.write_open_connection_request_1(new_packet), (options["ip"], options["port"]))
            recv = client_socket.recvfrom(65535)
            if recv[0][0] == packets.open_connection_reply_1["id"]:
                step = 1
        elif step == 1:
            new_packet = copy(packets.open_connection_request_2)
            new_packet["magic"] = options["magic"]
            new_packet["server_address"] = [options["ip"], options["port"]]
            new_packet["mtu_size"] = options["mtu_size"]
            new_packet["client_guid"] = options["guid"]
            client_socket.sendto(packets.write_open_connection_request_2(new_packet), (options["ip"], options["port"]))
            recv = client_socket.recvfrom(65535)
            if recv[0][0] == packets.open_connection_reply_2["id"]:
                step = 2
        elif step == 2:
            if connection["state"] == 1:
                new_packet = copy(packets.connection_request)
                new_packet["client_guid"] = options["guid"]
                new_packet["request_time"] = int(time.time())
                new_packet["use_security"] = 0
                send_packet = copy(packets.frame)
                send_packet["reliability"] = 2
                send_packet["reliable_index"] = connection["reliable_index"]
                connection["reliable_index"] += 1
                send_packet["body"] = packets.write_connection_request(new_packet)
                send_frame(send_packet)
            recv = client_socket.recvfrom(65535)
            if recv[0][0] == packets.ack["id"]:
                print("ACK")
            elif recv[0][0] == packets.nack["id"]:
                print("NACK")
            elif 0x80 <= recv[0][0] <= 0x8f:
                frame_set = packets.read_frame_set(recv[0])
                new_packet = copy(packets.ack)
                new_packet["packets"].append(frame_set["sequence_number"])
                client_socket.sendto(packets.write_acknowledgement(new_packet), (options["ip"], options["port"]))
                if frame_set["frame"]["body"][0] == packets.connection_request_accepted["id"] and connection["state"] == 1:
                    new_packet = copy(packets.new_connection)
                    new_packet["address"] = (options["ip"], options["port"])
                    new_packet["system_addresses"] = [("255.255.255.0", 19132)] * 10
                    new_packet["ping_time"] = int(time.time())
                    new_packet["pong_time"] = int(time.time())
                    send_packet = copy(packets.frame)
                    send_packet["reliability"] = 2
                    send_packet["reliable_index"] = connection["reliable_index"]
                    connection["reliable_index"] += 1
                    send_packet["body"] = packets.write_new_connection(new_packet)
                    send_frame(send_packet)
                    connection["state"] = 2
                elif frame_set["frame"]["body"][0] == packets.connection_closed["id"]:
                    connection["state"] == 0
                    break
                else:
                    options["custom_handler"](frame_set["frame"])
                new_packet = copy(packets.connected_ping)
                new_packet["time"] = int(time.time())
                send_packet = copy(packets.frame)
                send_packet["reliability"] = 2
                send_packet["reliable_index"] = connection["reliable_index"]
                connection["reliable_index"] += 1
                send_packet["body"] = packets.write_new_connection(new_packet)
                send_frame(send_packet)
