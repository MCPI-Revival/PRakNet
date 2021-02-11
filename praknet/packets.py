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

frame_set = {
    "id": 0x80,
    "sequence_number": None,
    "packets": []
}

frame = {
    "reliability": None,
    "is_fragmented": None,
    "length": None,
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

# Just to speed up the development

def read_address(data):
    address = ".".join([
        str(~data[1] & 0xff),
        str(~data[2] & 0xff),
        str(~data[3] & 0xff),
        str(~data[4] & 0xff)
    ])
    port = struct.unpack(">H", data[5:5 + 2])[0]
    return (addr, port)

def write_address(address):
    addr, port = address
    data = bytes([4])
    parts = addr.split(".")
    assert len(parts) == 4, f"Expected address length: 4, got {parts_count}"
    for part in parts:
        data += bytes([~int(part) & 0xff])
    data += struct.pack(">H", port)
    return data

# Decode and Encode PAckets

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

def read_unconnected_ping_open_connections(data):
    return {
        "id": data[0],
        "time": struct.unpack(">Q", data[1:1 + 8])[0],
        "magic": data[9:9 + 16]
    }

def write_unconnected_ping_open_connections(packet):
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
    data += bytes([packet["id"]])
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
    for i in range(0, 20):
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
        range = data[offset]
        offset += 1
        if range == 0:
            start_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            end_index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            index = start_index
            while index <= end_index:
                packet["packets"].append(index)
                if len(packet["packets"]) > 4096:
                    raise Exception("Max acknowledgement packet count exceed")
                index += 1
        else:
            index = struct.unpack('<L', data[offset:offset + 3] + b'\x00')[0]
            offset += 3
            packet["packets"].append(index)
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
        "length": 3,
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
    body_length = struct.unpack(">H", data[1:1 + 2])[0] >> 3
    if 2 <= packet["reliability"] <= 7 and packet["reliability"] != 5:
        packet["reliable_index"] = struct.unpack('<L', data[packet["length"]:packet["length"] + 3] + b'\x00')[0]
        packet["length"] += 3
    if packet["reliability"] == 1 or packet["reliability"] == 4:
        packet["sequence_index"] = struct.unpack('<L', data[packet["length"]:packet["length"] + 3] + b'\x00')[0]
        packet["length"] += 3
    if 1 <= packet["reliability"] <= 4 and packet["reliability"] != 2 or packet["reliability"] == 7:
        packet["order"]["index"] = struct.unpack('<L', data[packet["length"]:packet["length"] + 3] + b'\x00')[0]
        packet["length"] += 3
        packet["order"]["channel"] = data[packet["length"]]
        packet["length"] += 1
    if packet["is_fragmented"]:
        packet["fragment"]["size"] = struct.unpack('>l', data[packet["length"]:packet["length"] + 4])[0]
        packet["length"] += 4
        packet["fragment"]["id"] = struct.unpack('>H', data[packet["length"]:packet["length"] + 2])[0]
        packet["length"] += 2
        packet["fragment"]["index"] = struct.unpack('>l', data[packet["length"]:packet["length"] + 4])[0]
        packet["length"] += 4
    packet["body"] = data[packet["length"]:packet["length"] + body_length]
    packet["length"] += body_length
    return packet

# Just a small check point #

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
