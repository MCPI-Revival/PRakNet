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
        if client_protocol_version <= 5:
            packets.invalid_protocol_version["id"] = messages.ID_INCOMPATIBLE_PROTOCOL_VERSION_OLD
        packets.invalid_protocol_version["protocol_version"] = client_protocol_version
        packets.invalid_protocol_version["magic"] = packets.open_connection_request_1["magic"]
        packets.invalid_protocol_version["server_guid"] = server.options["server_guid"]
        return packets.write_invalid_protocol_version()
    packets.open_connection_reply_1["magic"] = packets.open_connection_request_1["magic"]
    packets.open_connection_reply_1["server_guid"] = server.options["server_guid"]
    packets.open_connection_reply_1["use_security"] = 0
    packets.open_connection_reply_1["mtu_size"] = packets.open_connection_request_1["mtu_size"]
    return packets.write_open_connection_reply_1()

def handle_open_connection_request_2(data, client_address):
    packets.read_open_connection_request_2(data)
    packets.open_connection_reply_2["magic"] = packets.open_connection_request_2["magic"]
    packets.open_connection_reply_2["server_guid"] = server.options["server_guid"]
    packets.open_connection_reply_2["client_address"] = client_address
    packets.open_connection_reply_2["mtu_size"] = packets.open_connection_request_2["mtu_size"]
    packets.open_connection_reply_2["use_security"] = 0
    server.add_connection(client_address[0], client_address[1])
    return packets.write_open_connection_reply_2()

def handle_connection_request(data, client_address):
    connection = server.get_connection(client_address[0], client_address[1])
    packets.read_encapsulated(data)
    packets.read_connection_request(packets.encapsulated["data_packet"])
    connection["client_guid"] = packets.connection_request["client_guid"]
    packets.connection_request_accepted["client_address"] = client_address
    packets.connection_request_accepted["system_index"] = 0
    packets.connection_request_accepted["system_addresses"] = []
    for i in range(0, 20):
        packets.connection_request_accepted["system_addresses"].append(("0.0.0.0", 0, 4))
    packets.connection_request_accepted["request_time"] = packets.connection_request["request_time"]
    packets.connection_request_accepted["time"] = int(time_now())
    packets.encapsulated["iteration"] = connection["iteration"]
    packets.encapsulated["encapsulation"] = 0x00
    packets.encapsulated["data_packet"] = packets.write_connection_request_accepted()
    return packets.write_encapsulated()

def handle_connected_ping(data, client_address):
    connection = server.get_connection(client_address[0], client_address[1])
    packets.read_encapsulated(data)
    packets.read_connected_ping(packets.encapsulated["data_packet"])
    packets.connected_pong["ping_time"] = packets.connected_ping["time"]
    packets.connected_pong["pong_time"] = int(time_now())
    packets.encapsulated["iteration"] = connection["iteration"]
    packets.encapsulated["encapsulation"] = 0x00
    packets.encapsulated["data_packet"] = packets.write_connected_pong()
    return packets.write_encapsulated()
