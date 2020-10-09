from praknet import messages
import struct

connected_ping = {
    "id": messages.ID_CONNECTED_PING,
    "time": None
}

unconnected_ping = {
    "id": messages.ID_UNCONNECTED_PING,
    "time": None,
    "magic": None,
    "client_guid": None
}

unconnected_ping_open_connections = {
    "id": messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS,
    "time": None,
    "magic": None,
    "client_guid": None
}

connected_pong = {
    "id": messages.ID_CONNECTED_PONG,
    "ping_time": None,
    "pong_time": None
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
    "encryption_enabled": None
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

connection_reply_accepted = {
    "id": messages.ID_CONNECTION_REPLY_ACCEPTED,
    "address": None,
    "system_addresses": [],
    "ping_time": None,
    "pong_time": None
}

connection_reply_canceled = {
    "id": messages.ID_CONNECTION_REPLY_CANCELED
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

encapsulated = {
    "iteration": None,
    "encapsulation": None,
    "length": None,
    "id": None,
    "data": None
}

@staticmethod
def read_unconnected_ping(data):
    unconnected_ping["id"] = data[0]
    unconnected_ping["time"] = struct.unpack(">Q", data[1:9])[0]
    unconnected_ping["magic"] = data[9:17]
    unconnected_ping["client_guid"] = struct.unpack(">Q", data[25:9])[0]
    
@staticmethod
def write_unconnected_ping():
    buffer = b""
    buffer += struct.pack(">B", unconnected_ping["id"])
    buffer += struct.pack(">Q", unconnected_ping["time"])
    buffer += unconnected_ping["magic"]
    buffer += struct.pack(">Q", unconnected_ping["client_guid"])
    return buffer

@staticmethod
def read_unconnected_ping_open_connections(data):
    unconnected_ping_open_connections["id"] = data[0]
    unconnected_ping_open_connections["time"] = struct.unpack(">Q", data[1:9])[0]
    unconnected_ping_open_connections["magic"] = data[9:17]
    unconnected_ping_open_connections["client_guid"] = struct.unpack(">Q", data[25:9])[0]
    
@staticmethod
def write_unconnected_ping():
    buffer = b""
    buffer += struct.pack(">B", unconnected_ping_open_connections["id"])
    buffer += struct.pack(">Q", unconnected_ping_open_connections["time"])
    buffer += unconnected_ping_open_connections["magic"]
    buffer += struct.pack(">Q", unconnected_ping_open_connections["client_guid"])
    return buffer
