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
from praknet import packets
from praknet import server
import struct

def encode_pos(pos):
    return struct.pack(">f", 128 + pos[0]) + struct.pack(">f", 64 + pos[1]) + struct.pack(">f", 128 + pos[2])

def decode_pos(pos):
    return [struct.unpack(">f", pos[:4])[0] - 128, struct.unpack(">f", pos[4:8])[0] - 64, struct.unpack(">f", pos[8:12])[0] - 128]

def custom_handler(packet, address):
    if "entities" not in server.options:
        server.options["entities"] = 0
    connection = server.get_connection(address)
    identifier = packet["body"][0]
    if identifier == 0x82:
        length = struct.unpack(">H", packet["body"][1:1 + 2])[0]
        connection["username"] = packet["body"][3:3 + length].decode()
        new_packet = b"\x83\x00\x00\x00\x00"
        send_packet = copy(packets.frame)
        send_packet["reliability"] = 0
        send_packet["body"] = new_packet
        server.send_frame(send_packet, address)
        server.options["entities"] += 1
        connection["entity_id"] = server.options["entities"]
        new_packet = b"\x87\x01\x02\x03\x04\x00\x00\x00\x00\x00\x00\x00\x01" + struct.pack(">l", server.options["entities"]) + encode_pos([0, 4, 0])
        connection["pos"] = [0, 4, 0]
        connection["yaw"] = 0
        connection["pitch"] = 0
        send_packet = copy(packets.frame)
        send_packet["reliability"] = 0
        send_packet["body"] = new_packet
        server.send_frame(send_packet, address)
    elif identifier == 0x94:
        connection["pos"] = decode_pos(packet["body"][5:5 + 12])
        connection["yaw"] = struct.unpack(">f", packet["body"][17:17 + 4])[0]
        connection["pitch"] = struct.unpack(">f", packet["body"][21:21 + 4])[0]
        if server.options["debug"]:
            message = "X: "
            message += str(connection["pos"][0])
            message += " Y: "
            message += str(connection["pos"][1])
            message += " Z: "
            message += str(connection["pos"][2])
            message += " YAW: "
            message += str(connection["yaw"])
            message += " PITCH: "
            message += str(connection["pitch"])
            new_packet = b"\x85" + struct.pack(">H", len(message)) + message.encode()
            send_packet = copy(packets.frame)
            send_packet["reliability"] = 0
            send_packet["body"] = new_packet
            server.send_frame(send_packet, address)
    elif identifier == 0x84:
        message = connection["username"] + " joined the game."
        new_packet = b"\x85" + struct.pack(">H", len(message)) + message.encode()
        send_packet = copy(packets.frame)
        send_packet["reliability"] = 0
        send_packet["body"] = new_packet
        server.broadcast_frame(send_packet)
        print(message)

server.options["custom_handler"] = custom_handler
server.options["name"] = "MCCPP;MINECON;PRakNet Test MCPI Server"
server.run()
