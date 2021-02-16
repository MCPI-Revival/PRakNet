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

from praknet import packets
from praknet import server
from time import time
from copy import copy

def handle_unconnected_ping(data):
    packet = packets.read_unconnected_ping(data)
    new_packet = copy(packets.unconnected_pong)
    new_packet["time"] = packet["time"]
    new_packet["server_guid"] = server.options["server_guid"]
    new_packet["magic"] = packet["magic"]
    new_packet["data"] = server.options["name"]
    return packets.write_unconnected_pong(new_packet)

def handle_open_connection_request_1(data):
    packet = packets.read_open_connection_request_1(data)
    if packet["protocol_version"] not in server.options["accepted_raknet_protocols"]:
        new_packet = copy(packets.invalid_protocol_version)
        new_packet["protocol_version"] = packet["protocol_version"]
        new_packet["magic"] = packet["magic"]
        new_packet["server_guid"] = server.options["server_guid"]
        return packets.write_invalid_protocol_version(new_packet)
    new_packet = copy(packets.open_connection_reply_1)
    new_packet["magic"] = packet["magic"]
    new_packet["server_guid"] = server.options["server_guid"]
    new_packet["use_security"] = 0
    new_packet["mtu_size"] = packet["mtu_size"]
    return packets.write_open_connection_reply_1(new_packet)

def handle_open_connection_request_2(data, address):
    packet = packets.read_open_connection_request_2(data)
    new_packet = copy(packets.open_connection_reply_2)
    new_packet["magic"] = packet["magic"]
    new_packet["server_guid"] = server.options["server_guid"]
    new_packet["client_address"] = address
    new_packet["mtu_size"] = packet["mtu_size"]
    new_packet["use_security"] = 0
    server.add_connection(address)
    server.get_connection(address)["mtu_size"] = packet["mtu_size"]
    return packets.write_open_connection_reply_2(new_packet)

def handle_connection_request(data, address):
    packet = packets.read_connection_request(data)
    new_packet = copy(packets.connection_request_accepted)
    new_packet["client_address"] = address
    new_packet["system_index"] = 0
    new_packet["system_addresses"] = [("255.255.255.255", 19132)] * 10
    new_packet["request_time"] = packet["request_time"]
    new_packet["time"] = int(time())
    server.get_connection(address)["guid"] = packet["client_guid"]
    return packets.write_connection_request_accepted(new_packet)

def handle_connected_ping(data):
    packet = packets.read_connected_ping(data)
    new_packet = copy(packets.connected_pong)
    new_packet["time"] = packet["time"]
    return packets.write_connected_pong(new_packet)
