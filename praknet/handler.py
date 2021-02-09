from praknet import messages
from praknet import packets
from praknet import server
from time import time as time_now

def handle_unconnected_ping(data):
    packets.read_unconnected_ping(data)
    packets.unconnected_pong["time"] = packets.unconnected_ping["time"]
    packets.unconnected_pong["server_guid"] = server.options["server_guid"]
    packets.unconnected_pong["magic"] = packets.unconnected_ping["magic"]
    packets.unconnected_pong["data"] = server.options["name"]
    return packets.write_unconnected_pong()

def handle_unconnected_ping_open_connections(data):
    packets.read_unconnected_ping_open_connections(data)
    packets.unconnected_pong["time"] = packets.unconnected_ping_open_connections["time"]
    packets.unconnected_pong["server_guid"] = server.options["server_guid"]
    packets.unconnected_pong["magic"] = packets.unconnected_ping_open_connections["magic"]
    packets.unconnected_pong["data"] = server.options["name"]
    return packets.write_unconnected_pong()

def handle_open_connection_request_1(data):
    packets.read_open_connection_request_1(data)
    client_protocol_version = packets.open_connection_request_1["protocol_version"]
    if not client_protocol_version in server.options["accepted_raknet_protocols"]:
        packets.invalid_protocol_version["id"] = messages.ID_INCOMPATIBLE_PROTOCOL_VERSION
        packets.invalid_protocol_version["protocol_version"] = client_protocol_version
        packets.invalid_protocol_version["magic"] = packets.open_connection_request_1["magic"]
        packets.invalid_protocol_version["server_guid"] = server.options["server_guid"]
        return packets.write_invalid_protocol_version()
    packets.open_connection_reply_1["magic"] = packets.open_connection_request_1["magic"]
    packets.open_connection_reply_1["server_guid"] = server.options["server_guid"]
    packets.open_connection_reply_1["use_security"] = 0
    packets.open_connection_reply_1["mtu_size"] = packets.open_connection_request_1["mtu_size"]
    return packets.write_open_connection_reply_1()

def handle_open_connection_request_2(data, address):
    packets.read_open_connection_request_2(data)
    packets.open_connection_reply_2["magic"] = packets.open_connection_request_2["magic"]
    packets.open_connection_reply_2["server_guid"] = server.options["server_guid"]
    packets.open_connection_reply_2["client_address"] = address
    packets.open_connection_reply_2["mtu_size"] = packets.open_connection_request_2["mtu_size"]
    packets.open_connection_reply_2["use_security"] = 0
    server.add_connection(address[0], address[1])
    server.get_connection(address[0], address[1])["mtu_size"] = packets.open_connection_reply_2["mtu_size"]
    return packets.write_open_connection_reply_2()

def handle_connection_request(data, connection):
    packets.read_connection_request(data)
    packets.connection_request_accepted["client_address"] = connection["address"]
    packets.connection_request_accepted["system_index"] = 0
    packets.connection_request_accepted["system_addresses"] = []
    for i in range(0, 20):
        packets.connection_request_accepted["system_addresses"].append(("0.0.0.0", 0, 4))
    packets.connection_request_accepted["request_time"] = packets.connection_request["request_time"]
    packets.connection_request_accepted["time"] = int(time_now())
    return packets.write_connection_request_accepted()

def handle_connected_ping(data):
    packets.read_connected_ping(data)
    packets.connected_pong["time"] = packets.connected_ping["time"]
    return packets.write_connected_pong()
