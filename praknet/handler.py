from praknet import packets
from praknet import server

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
    packets.open_connection_reply_1["magic"] = packets.open_connection_request_1["magic"]
    packets.open_connection_reply_1["server_guid"] = server.options["server_guid"]
    packets.open_connection_reply_1["use_security"] = 0
    packets.open_connection_reply_1["mtu_size"] = packets.open_connection_request_1["mtu_size"]
    return packets.write_open_connection_reply_1()
