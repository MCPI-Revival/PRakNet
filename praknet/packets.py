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

import struct

# Packet ids

id_connected_ping = 0x00
id_unconnected_ping = 0x01
id_unconnected_ping_open_connections = 0x02
id_connected_pong = 0x03
id_open_connection_request_1 = 0x05
id_open_connection_reply_1 = 0x06
id_open_connection_request_2 = 0x07
id_open_connection_reply_2 = 0x08
id_connection_request = 0x09
id_connection_request_accepted = 0x10
id_new_connection = 0x13
id_connection_closed = 0x15
id_invalid_protocol_version = 0x1a
id_unconnected_pong = 0x1c
id_advertise_system = 0x1d,
id_nack = 0xa0
id_ack = 0xc0
id_frame_set = 0x80

# Utils

def read_address(data):
    address = ".".join([
        str(~data[1] & 0xff),
        str(~data[2] & 0xff),
        str(~data[3] & 0xff),
        str(~data[4] & 0xff)
    ])
    port = struct.unpack(">H", data[5:5 + 2])[0]
    return (address, port)

def write_address(address):
    data = bytes([4])
    parts = address[0].split(".")
    assert len(parts) == 4, "Expected address length: 4, got " + str(parts_count)
    for part in parts:
        data += bytes([~int(part) & 0xff])
    data += struct.pack(">H", address[1])
    return data

def read_var_int(data):
    result = 0
    pos = 0
    for i in range(0, 35, 7):
        if len(data) <= pos:
            raise Exception("Data position exceeded")
        byte = data[pos]
        pos += 1
        result |= ((byte & 0x7f) << i)
        if (byte & 0x80) == 0:
            return result
    raise Exception("VarInt is too big")
    
def read_var_long(data):
    result = 0
    pos = 0
    for i in range(0, 70, 7):
        if len(data) <= pos:
            raise Exception("Data position exceeded")
        byte = data[pos]
        pos += 1
        result |= ((byte & 0x7f) << i)
        if (byte & 0x80) == 0:
            return result
    raise Exception("VarLong is too big")
    
def read_signed_var_int(data):
    raw = read_var_int(data)
    return -(raw >> 1) - 1 if (raw & 1) else raw >> 1

def read_signed_var_long(data):
    raw = read_var_long(data)
    return -(raw >> 1) - 1 if (raw & 1) else raw >> 1

# Decode and Encode Packets

def read_connected_ping(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0]
    }

def write_connected_ping(packet):
    data = bytes([packet["id"]])
    data += struct.pack(">Q", packet["time"])
    return data

def read_unconnected_ping(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0],
        "magic": data[9:9 + 16]
    }

def write_unconnected_ping(packet):
    data = bytes([packet["id"]])
    data += struct.pack(">Q", packet["time"])
    data += packet["magic"]
    return data

def read_connected_pong(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0]
    }

def write_connected_pong(packet):
    data = bytes([packet["id"]])
    data += struct.pack(">Q", packet["time"])
    return data

def read_open_connection_request_1(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "protocol_version": data[17],
        "mtu_size": len(data[18:]) + 46
    }

def write_open_connection_request_1(packet):
    data = bytes([packet["id"]])
    data += packet["magic"]
    data += bytes([packet["protocol_version"]])
    data += b"\x00" * (packet["mtu_size"] - 46)
    return data

def read_open_connection_reply_1(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "server_guid": struct.unpack(">Q", data[17:17 + 8])[0],
        "use_security": data[25],
        "mtu_size": struct.unpack(">H", data[26:26 + 2])[0]
    }

def write_open_connection_reply_1(packet):
    data = bytes([packet["id"]])
    data += packet["magic"]
    data += struct.pack(">Q", packet["server_guid"])
    data += bytes([packet["use_security"]])
    data += struct.pack(">H", packet["mtu_size"])
    return data

def read_open_connection_request_2(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "server_address": read_address(data[17:17 + 7]),
        "mtu_size": struct.unpack(">H", data[24:24 + 2])[0],
        "client_guid": struct.unpack(">Q", data[26:26 + 8])[0]
    }

def write_open_connection_request_2(packet):
    data = bytes([packet["id"]])
    data += packet["magic"]
    data += write_address(packet["server_address"])
    data += struct.pack(">H", packet["mtu_size"])
    data += struct.pack(">Q", packet["client_guid"])
    return data

def read_open_connection_reply_2(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "server_guid": struct.unpack(">Q", data[17:17 + 8])[0],
        "client_address": read_address(data[25:25 + 7]),
        "mtu_size": struct.unpack(">H", data[32:32 + 2])[0],
        "use_security": data[34]
    }

def write_open_connection_reply_2(packet):
    data = bytes([packet["id"]])
    data += packet["magic"]
    data += struct.pack(">Q", packet["server_guid"])
    data += write_address(packet["client_address"])
    data += struct.pack(">H", packet["mtu_size"])
    data += bytes([packet["use_security"]])
    return data

def read_connection_request(data):
    return {
        "id": data[0],
        "client_guid": struct.unpack(">Q", data[1:1 + 8])[0],
        "request_time": struct.unpack(">Q", data[9:9 + 8])[0],
        "use_security": data[17]
    }

def write_connection_request(packet):
    data = bytes([packet["id"]])
    data += struct.pack(">Q", packet["client_guid"])
    data += struct.pack(">Q", packet["request_time"])
    data += bytes([packet["use_security"]])
    return data

def read_connection_request_accepted(data):
    packet = {
        "id": data[0],
        "client_address": read_address(data[1:1 + 7]),
        "system_index": data[8],
        "system_addresses": [],
        "request_time": struct.unpack(">Q", data[79:79 + 8])[0],
        "time": struct.unpack(">Q", data[87:87 + 8])[0]
    }
    offset = 9
    for i in range(0, 10):
        packet["system_addresses"].append(read_address(data[offset:offset + 7]))
        offset += 7
    return packet

def write_connection_request_accepted(packet):
    data = bytes([packet["id"]])
    data += write_address(packet["client_address"])
    data += bytes([packet["system_index"]])
    for i in range(0, 10):
        data += write_address(packet["system_addresses"][i])
    data += struct.pack(">Q", packet["request_time"])
    data += struct.pack(">Q", packet["time"])
    return data

def read_new_connection(data):
    packet = {
        "id": data[0],
        "address": read_address(data[1:1 + 7]),
        "system_addresses": [],
        "ping_time": struct.unpack(">Q", data[78:78 + 8])[0],
        "pong_time": struct.unpack(">Q", data[86:86 + 8])[0]
    }
    offset = 8
    for i in range(0, 10):
        packet["system_addresses"].append(read_address(data[offset:offset + 7]))
        offset += 7
    return packet

def write_new_connection(packet):
    data = bytes([packet["id"]])
    data += write_address(packet["address"])
    for i in range(0, 10):
        data += write_address(packet["system_addresses"][i])
    data += struct.pack(">Q", packet["ping_time"])
    data += struct.pack(">Q", packet["pong_time"])
    return data

def read_invalid_protocol_version(data):
    return {
        "id": data[0],
        "protocol_version": data[1],
        "magic": data[2:2 + 16],
        "server_guid": struct.unpack(">Q", data[18:18 + 8])[0]
    }

def write_invalid_protocol_version(packet):
    data = bytes([packet["id"]])
    data += bytes([packet["protocol_version"]])
    data += packet["magic"]
    data += struct.pack(">Q", packet["server_guid"])
    return data

def read_unconnected_pong(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0],
        "server_guid": struct.unpack(">Q", data[9:9 + 8]),
        "magic": data[17:17 + 16],
        "data": data[35:35 + struct.unpack(">H", data[33:33 + 2])[0]].decode()
    }

def write_unconnected_pong(packet):
    data = bytes([packet["id"]])
    data += struct.pack(">Q", packet["time"])
    data += struct.pack(">Q", packet["server_guid"])
    data += packet["magic"]
    data += struct.pack(">H", len(packet["data"]))
    data += packet["data"].encode()
    return data

def read_acknowledgement(data):
    packet = {
        "id": data[0],
        "packets": []
    }
    count = struct.unpack(">H", data[1:1 + 2])[0]
    offset = 3
    for i in range(0, count):
        is_single = data[offset] > 0
        offset += 1
        if not is_single:
            packet["packets"].append(struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0])
            offset += 3
            packet["packets"].append(struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0])
            offset += 3
        else:
            packet["packets"].append(struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0])
            offset += 3
    return packet

def write_acknowledgement(packet):
    data = bytes([packet["id"]])
    records = 0
    packet["packets"].sort()
    if len(packet["packets"]) > 0:
        pointer = 1
        start_index = packet["packets"][0]
        end_index = packet["packets"][0]
        while pointer < len(packet["packets"]):
            index = packet["packets"][pointer]
            pointer += 1
            diff = index - end_index
            if diff == 1:
                end_index = index
            elif diff > 1:
                if start_index == end_index:
                    data += b"\x01"
                    data += struct.pack("<L", start_index)[0:-1]
                    start_index = end_index = index
                else:
                    data += b"\x00"
                    data += struct.pack("<L", start_index)[0:-1]
                    data += struct.pack("<L", end_index)[0:-1]
                    start_index = end_index = index
                records += 1
        if start_index == end_index:
            data += b"\x01"
            data += struct.pack("<L", start_index)[0:-1]
        else:
            data += b"\x00"
            data += struct.pack("<L", start_index)[0:-1]
            data += struct.pack("<L", end_index)[0:-1]
        records += 1
    data = data[0:1] + struct.pack(">H", records) + data[1:]
    return data

def read_frame(data):
    packet = {
        "reliability": (data[0] & 224) >> 5,
        "is_fragmented": (data[0] & 0x10) > 0,
        "reliable_index": None,
        "sequence_index": None,
        "order": {
            "index": None,
            "channel": None
        },
        "fragment": {
            "size": None,
            "id": None,
            "index": None
        },
        "body": None
    }
    offset = 3
    if 2 <= packet["reliability"] <= 7 and packet["reliability"] != 5:
        packet["reliable_index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
    if packet["reliability"] == 1 or packet["reliability"] == 4:
        packet["sequence_index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
    if 1 <= packet["reliability"] <= 4 and packet["reliability"] != 2 or packet["reliability"] == 7:
        packet["order"]["index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
        packet["order"]["channel"] = data[offset]
        offset += 1
    if packet["is_fragmented"]:
        packet["fragment"]["size"] = struct.unpack('>l', data[offset:offset + 4])[0]
        offset += 4
        packet["fragment"]["id"] = struct.unpack('>H', data[offset:offset + 2])[0]
        offset += 2
        packet["fragment"]["index"] = struct.unpack('>l', data[offset:offset + 4])[0]
        offset += 4
    length = struct.unpack(">H", data[1:1 + 2])[0] >> 3
    packet["body"] = data[offset:offset + length]
    offset += length
    return packet

def write_frame(packet):
    flags = packet["reliability"] << 5
    if packet["is_fragmented"]:
        flags |= 0x10
    data = bytes([flags])
    data += struct.pack(">H", len(packet["body"]) << 3)
    if 2 <= packet["reliability"] <= 7 and packet["reliability"] != 5:
        data += struct.pack("<L", packet["reliable_index"])[0:-1]
    if packet["reliability"] == 1 or packet["reliability"] == 4:
        data += struct.pack("<L", packet["sequence_index"])[0:-1]
    if 1 <= packet["reliability"] <= 4 and packet["reliability"] != 2 or packet["reliability"] == 7:
        data += struct.pack("<L", packet["order"]["index"])[0:-1]
        data += bytes([packet["order"]["channel"]])
    if packet["is_fragmented"]:
        data += struct.pack(">l", packet["fragment"]["size"])
        data += struct.pack(">H", packet["fragment"]["id"])
        data += struct.pack(">l", packet["fragment"]["index"])
    data += packet["body"]
    return data

def read_frame_set(data):
    packet = {
        "id": data[0],
        "sequence_number": struct.unpack('<L', data[1:1 + 3] + b'\x00')[0],
        "frames": []
    }
    offset = 4
    while not len(data) <= offset:
        frame = read_frame(data[offset:])
        offset += 3
        if frame["reliable_index"] is not None:
            offset += 3
        if frame["sequence_index"] is not None:
            offset += 3
        if frame["order"]["index"] is not None:
            offset += 4
        if frame["is_fragmented"]:
            offset += 10
        offset += len(frame["body"])
        packet["frames"].append(frame)
        return packet

def write_frame_set(packet):
    data = bytes([packet["id"]])
    data += struct.pack("<L", packet["sequence_number"])[0:-1]
    for frame in packet["frames"]:
        data += write_frame(frame)
    return data
