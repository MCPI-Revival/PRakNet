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

from praknet import messages
from praknet import reliability
import struct

# Packet templates

connected_ping = {
    "id": messages.ID_CONNECTED_PING,
    "time": None
}

unconnected_ping = {
    "id": messages.ID_UNCONNECTED_PING,
    "time": None,
    "magic": None
}

unconnected_ping_open_connections = {
    "id": messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS,
    "time": None,
    "magic": None
}

connected_pong = {
    "id": messages.ID_CONNECTED_PONG,
    "time": None
}

open_connection_request_1 = {
    "id": messages.ID_OPEN_CONNECTION_REQUEST_1,
    "magic": None,
    "protocol_version": None,
    "mtu_size": None
}

open_connection_reply_1 = {
    "id": messages.ID_OPEN_CONNECTION_REPLY_1,
    "magic": None,
    "server_guid": None,
    "use_security": None,
    "mtu_size": None
}

open_connection_request_2 = {
    "id": messages.ID_OPEN_CONNECTION_REQUEST_2,
    "magic": None,
    "server_address": None,
    "mtu_size": None,
    "client_guid": None
}

open_connection_reply_2 = {
    "id": messages.ID_OPEN_CONNECTION_REPLY_2,
    "magic": None,
    "server_guid": None,
    "client_address": None,
    "mtu_size": None,
    "use_security": None
}

connection_request = {
    "id": messages.ID_CONNECTION_REQUEST,
    "client_guid": None,
    "request_time": None,
    "use_security": None
}

connection_request_accepted = {
    "id": messages.ID_CONNECTION_REQUEST_ACCEPTED,
    "client_address": None,
    "system_index": None,
    "system_addresses": [],
    "request_time": None,
    "time": None
}

new_connection = {
    "id": messages.ID_NEW_CONNECTION,
    "address": None,
    "system_addresses": [],
    "ping_time": None,
    "pong_time": None
}

connection_closed = {
    "id": messages.ID_CONNECTION_CLOSED
}

invalid_protocol_version = {
    "id": messages.ID_INCOMPATIBLE_PROTOCOL_VERSION,
    "protocol_version": None,
    "magic": None,
    "server_guid": None
}

unconnected_pong = {
    "id": messages.ID_UNCONNECTED_PONG,
    "time": None,
    "server_guid": None,
    "magic": None,
    "data": None
}

advertise_system = {
    "id": messages.ID_ADVERTISE_SYSTEM,
    "time": None,
    "server_guid": None,
    "magic": None,
    "data": None
}

nack = {
    "id": messages.ID_NACK,
    "packets": [],
}

ack = {
    "id": messages.ID_ACK,
    "packets": []
}

encapsulated = {
    "is_fragmented": None,
    "need_ack": None,
    "sequence_order": None,
    "flags": None,
    "length": None,
    "reliable_frame_index": None,
    "sequenced_frame_index": None,
    "order": {
        "ordered_frame_index": None,
        "order_channel": None
    },
    "fragment": {
        "compound_size": None,
        "compound_id": None,
        "index": None
    },
    "body": None
}

# Just to speed up the development

def read_address(data):
    addr = ".".join([
        str((~struct.unpack(">B", data[1:1 + 1])[0]) & 0xff),
        str((~struct.unpack(">B", data[2:2 + 1])[0]) & 0xff),
        str((~struct.unpack(">B", data[3:3 + 1])[0]) & 0xff),
        str((~struct.unpack(">B", data[4:4 + 1])[0]) & 0xff)
    ])
    port = struct.unpack(">H", data[5:5 + 2])[0]
    return (addr, port)

def write_address(address):
    addr, port = address
    data = struct.pack(">B", 4)
    parts = addr.split(".")
    assert len(parts) == 4, f"Expected address length: 4, got {parts_count}"
    for part in parts:
        data += struct.pack(">B", (~(int(part))) & 0xff)
    data += struct.pack(">H", port)
    return data

# Decode and Encode PAckets

def read_connected_ping(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0]
    }

def write_connected_ping(packet):
    data = struct.pack(">B", packet["id"])
    data += struct.pack(">Q", packet["time"])
    return data

def read_unconnected_ping(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0],
        "magic": data[9:9 + 16]
    }

def write_unconnected_ping(packet):
    data = struct.pack(">B", packet["id"])
    data += struct.pack(">Q", packet["time"])
    data += packet["magic"]
    return data

def read_unconnected_ping_open_connections(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0],
        "magic": data[9:9 + 16]
    }

def write_unconnected_ping_open_connections(packet):
    data = struct.pack(">B", packet["id"])
    data += struct.pack(">Q", packet["time"])
    data += packet["magic"]
    return data

def read_connected_pong(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0]
    }

def write_connected_pong(packet):
    data = struct.pack(">B", packet["id"])
    data += struct.pack(">Q", packet["time"])
    return data

def read_open_connection_request_1(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "protocol_version": struct.unpack(">B", data[17:17 + 1])[0],
        "mtu_size": len(data[18:]) + 46
    }

def write_open_connection_request_1(packet):
    data = struct.pack(">B", packet["id"])
    data += packet["magic"]
    data += struct.pack(">B", packet["protocol_version"])
    data += b"\x00" * (packet["mtu_size"] - 46)
    return data

def read_open_connection_reply_1(data):
    return {
        "id": data[0],
        "magic": data[1:1 + 16],
        "server_guid": struct.unpack(">Q", data[17:17 + 8])[0],
        "use_security": struct.unpack(">B", data[25:25 + 1])[0],
        "mtu_size": struct.unpack(">H", data[26:26 + 2])[0]
    }

def write_open_connection_reply_1(packet):
    data = struct.pack(">B", packet["id"])
    data += packet["magic"]
    data += struct.pack(">Q", packet["server_guid"])
    data += struct.pack(">B", packet["use_security"])
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
    data = struct.pack(">B", packet["id"])
    data += packet["magic"]
    data += write_address(packet["server_address"])
    data += struct.pack(">H", packet["mtu_size"])
    data += struct.pack(">Q", packet["client_guid"])
    return data

def read_open_connection_reply_2(data):
    packet = {
        "id": data[0],
        "magic": data[1:1 + 16],
        "server_guid": struct.unpack(">Q", data[17:17 + 8])[0],
        "client_address": read_address(data[25:25 + 7]),
        "mtu_size": struct.unpack(">H", data[32:32 + 2])[0],
        "use_security": struct.unpack(">B", data[34:34 + 1])[0]
    }

def write_open_connection_reply_2(packet):
    data = struct.pack(">B", packet["id"])
    data += packet["magic"]
    data += struct.pack(">Q", packet["server_guid"])
    data += write_address(packet["client_address"])
    data += struct.pack(">H", packet["mtu_size"])
    data += struct.pack(">B", packet["use_security"])
    return data

def read_connection_request(data):
    return {
        "id": data[0],
        "client_guid": struct.unpack(">Q", data[1:1 + 8])[0],
        "request_time": struct.unpack(">Q", data[9:9 + 8])[0],
        "use_security": struct.unpack(">B", data[17:17 + 1])[0]
    }

def write_connection_request(packet):
    data += struct.pack(">B", packet["id"])
    data += struct.pack(">Q", packet["client_guid"])
    data += struct.pack(">Q", packet["request_time"])
    data += struct.pack(">B", packet["use_security"])
    return data

# Just a small check point #

def read_connection_request_accepted(data):
    connection_request_accepted["id"] = data[0]
    connection_request_accepted["client_address"] = read_address(data[1:1 + 7])
    connection_request_accepted["system_index"] = struct.unpack(">B", data[8:8 + 1])[0]
    offset = 9
    for i in range(0, 20):
        connection_request_accepted["system_addresses"].append(read_address(data[offset:offset + 7]))
        offset += 7
    connection_request_accepted["request_time"] = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8
    connection_request_accepted["time"] = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8

def write_connection_request_accepted():
    buffer = b""
    buffer += struct.pack(">B", connection_request_accepted["id"])
    buffer += write_address(connection_request_accepted["client_address"])
    buffer += struct.pack(">B", connection_request_accepted["system_index"])
    for i in range(0, 10):
        buffer += write_address(connection_request_accepted["system_addresses"][i])
    buffer += struct.pack(">Q", connection_request_accepted["request_time"])
    buffer += struct.pack(">Q", connection_request_accepted["time"])
    return buffer

def read_new_connection(data):
    new_connection["id"] = data[0]
    new_connection["address"] = read_address(data[1:1 + 7])
    offset = 8
    for i in range(0, 10):
        new_connection["system_addresses"].append(read_address(data[offset:offset + 7]))
        offset += 7
    new_connection["ping_time"] = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8
    new_connection["pong_time"] = struct.unpack(">Q", data[offset:offset + 8])[0]
    offset += 8

def write_new_connection():
    buffer = b""
    buffer += struct.pack(">B", new_connection["id"])
    buffer += write_address(new_connection["address"])
    for i in range(0, 20):
        buffer += write_address(new_connection["system_addresses"][i])
    buffer += struct.pack(">Q", new_connection["ping_time"])
    buffer += struct.pack(">Q", new_connection["pong_time"])
    return buffer

def read_invalid_protocol_version(data):
    invalid_protocol_version["id"] = data[0]
    invalid_protocol_version["protocol_version"] = data[1]
    invalid_protocol_version["magic"] = data[2:2 + 16]
    invalid_protocol_version["server_guid"] = struct.unpack(">Q", data[18:18 + 8])[0]

def write_invalid_protocol_version():
    buffer = b""
    buffer += struct.pack(">B", invalid_protocol_version["id"])
    buffer += struct.pack(">B", invalid_protocol_version["protocol_version"])
    buffer += invalid_protocol_version["magic"]
    buffer += struct.pack(">Q", invalid_protocol_version["server_guid"])
    return buffer

def read_unconnected_pong(data):
    unconnected_pong["id"] = data[0]
    unconnected_pong["time"] = struct.unpack(">Q", data[1:1 + 8])[0]
    unconnected_pong["server_guid"] = struct.unpack(">Q", data[9:9 + 8])
    unconnected_pong["magic"] = data[17:17 + 16]
    unconnected_pong["data"] = data[35:35 + struct.unpack(">H", data[33:33 + 2])[0]].decode()

def write_unconnected_pong():
    buffer = b""
    buffer += struct.pack(">B", unconnected_pong["id"])
    buffer += struct.pack(">Q", unconnected_pong["time"])
    buffer += struct.pack(">Q", unconnected_pong["server_guid"])
    buffer += unconnected_pong["magic"]
    buffer += struct.pack(">H", len(unconnected_pong["data"]))
    buffer += unconnected_pong["data"].encode()
    return buffer

def read_nack(data):
    nack["id"] = data[0]
    nack["packets"] = []
    count = struct.unpack(">H", data[1:1 + 2])[0]
    offset = 3
    for i in range(0, count):
        range = struct.unpack(">B", data[offset:offset + 1])
        offset += 1
        if range == 0:
            start_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            end_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            index = start_index
            while index <= end_index:
                nack["packets"].append(index)
                if len(nack["packets"]) > 4096:
                    raise Exception("Max acknowledgement packet count exceed")
                index += 1
        else:
            index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            nack["packets"].append(index)

def write_nack():
    buffer = b""
    buffer += struct.pack(">B", nack["id"])
    records = 0
    nack["packets"].sort()
    if len(nack["packets"]) > 0:
        pointer = 1
        start_index = nack["packets"][0]
        end_index = nack["packets"][0]
        while pointer < len(nack["packets"]):
            index = nack["packets"][pointer]
            pointer += 1
            diff = index - end_index
            if diff == 1:
                end_index = index
            elif diff > 1:
                if start_index == end_index:
                    buffer += struct.pack(">B", 1)
                    buffer += struct.pack("<L", start_index)[0:-1]
                    start_index = end_index = index
                else:
                    buffer += struct.pack(">B", 0)
                    buffer += struct.pack("<L", start_index)[0:-1]
                    buffer += struct.pack("<L", end_index)[0:-1]
                    start_index = end_index = index
                records += 1
        if start_index == end_index:
            buffer += struct.pack(">B", 1)
            buffer += struct.pack("<L", start_index)[0:-1]
        else:
            buffer += struct.pack(">B", 0)
            buffer += struct.pack("<L", start_index)[0:-1]
            buffer += struct.pack("<L", end_index)[0:-1]
        records += 1
    buffer = buffer[0:1] + struct.pack(">H", records) + buffer[1:]
    return buffer

def read_ack(data):
    ack["id"] = data[0]
    ack["packets"] = []
    count = struct.unpack(">H", data[1:1 + 2])[0]
    offset = 3
    for i in range(0, count):
        range = struct.unpack(">B", data[offset:offset + 1])
        offset += 1
        if range == 0:
            start_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            end_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            index = start_index
            while index <= end_index:
                ack["packets"].append(index)
                if len(ack["packets"]) > 4096:
                    raise Exception("Max acknowledgement packet count exceed")
                index += 1
        else:
            index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            ack["packets"].append(index)

def write_ack():
    buffer = b""
    buffer += struct.pack(">B", ack["id"])
    records = 0
    ack["packets"].sort()
    if len(ack["packets"]) > 0:
        pointer = 1
        start_index = ack["packets"][0]
        end_index = ack["packets"][0]
        while pointer < len(ack["packets"]):
            index = ack["packets"][pointer]
            pointer += 1
            diff = index - end_index
            if diff == 1:
                end_index = index
            elif diff > 1:
                if start_index == end_index:
                    buffer += struct.pack(">B", 1)
                    buffer += struct.pack("<L", start_index)[0:-1]
                    start_index = end_index = index
                else:
                    buffer += struct.pack(">B", 0)
                    buffer += struct.pack("<L", start_index)[0:-1]
                    buffer += struct.pack("<L", end_index)[0:-1]
                    start_index = end_index = index
                records += 1
        if start_index == end_index:
            buffer += struct.pack(">B", 1)
            buffer += struct.pack("<L", start_index)[0:-1]
        else:
            buffer += struct.pack(">B", 0)
            buffer += struct.pack("<L", start_index)[0:-1]
            buffer += struct.pack("<L", end_index)[0:-1]
        records += 1
    buffer = buffer[0:1] + struct.pack(">H", records) + buffer[1:]
    return buffer

def read_encapsulated(data):
    offset = 1
    encapsulated["sequence_order"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
    offset += 3
    flags = struct.unpack(">B", data[offset:offset + 1])[0]
    offset += 1
    encapsulated["flags"] = (flags & 224) >> 5
    encapsulated["is_fragmented"] = (flags & 0x10) > 0
    encapsulated["length"] = struct.unpack(">H", data[offset:offset + 2])[0] >> 3
    offset += 2
    if reliability.is_reliable(encapsulated["flags"]):
        encapsulated["reliable_frame_index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
    if reliability.is_sequenced(encapsulated["flags"]):
        encapsulated["sequenced_frame_index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
    if reliability.is_sequenced_or_ordered(encapsulated["flags"]):
        encapsulated["order"]["ordered_frame_index"] = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
        offset += 3
        encapsulated["order"]["order_channel"] = struct.unpack(">B", data[offset:offset + 1])[0]
        offset += 1
    if encapsulated["is_fragmented"]:
        encapsulated["fragment"]["compound_size"] = struct.unpack('>l', data[offset:offset + 4])[0]
        offset += 4
        encapsulated["fragment"]["compound_id"] = struct.unpack(">H", data[offset:offset + 2])[0]
        offset += 2
        encapsulated["fragment"]["index"] = struct.unpack('>l', data[offset:offset + 4])[0]
        offset += 4
    encapsulated["body"] = data[offset:offset + encapsulated["length"]]
    offset += encapsulated["length"]

def write_encapsulated():
    buffer = b""
    buffer += b"\x80"
    buffer += struct.pack("<L", encapsulated["sequence_order"])[0:-1]
    flags = encapsulated["flags"] << 5
    if encapsulated["is_fragmented"]:
        flags |= 0x10
    buffer += struct.pack(">B", flags)
    buffer += struct.pack(">H", len(encapsulated["body"]) << 3)
    if reliability.is_reliable(encapsulated["flags"]):
        buffer += struct.pack("<L", encapsulated["reliable_frame_index"])[0:-1]
    if reliability.is_sequenced(encapsulated["flags"]):
        buffer += struct.pack("<L", encapsulated["sequenced_frame_index"])[0:-1]
    if reliability.is_sequenced_or_ordered(encapsulated["flags"]):
        buffer += struct.pack("<L", encapsulated["order"]["ordered_frame_index"])[0:-1]
        buffer += struct.pack(">B", encapsulated["order"]["order_channel"])
    if encapsulated["is_fragmented"]:
        buffer += struct.pack(">l", encapsulated["fragment"]["compound_size"])
        buffer += struct.pack(">H", encapsulated["fragment"]["compound_id"])
        buffer += struct.pack(">l", encapsulated["fragment"]["index"])
    buffer += encapsulated["body"]
    return buffer
