import os
from praknet import handler
from praknet import messages
from praknet import packets
from praknet import socket
import struct

options = {
    "name": "",
    "ip": "0.0.0.0",
    "port": 19132,
    "server_guid": struct.unpack(">q", os.urandom(8))[0],
    "custom_handler": lambda data, addr: 0,
    "accepted_raknet_protocols": [5, 6, 7, 8, 9, 10]
}

status = {
    "connecting": 0,
    "connected": 1,
    "disconnecting": 2,
    "disconnected": 3
}

connections = {}

def add_connection(addr, port):
    token = str(addr) + ":" + str(port)
    connections[token] = {
        "client_guid": 0,
        "mtu_size": 0,
        "address": (addr, port, 4),
        "connecton_state": status["connecting"],
        "packets_queue": [],
        "sequence_order": 0
    }

def remove_connection(addr, port):
    token = str(addr) + ":" + str(port)
    if token in connections:
        del connections[token]

def get_connection(addr, port):
    token = str(addr) + ":" + str(port)
    if token in connections:
        return connections[token]
    else:
        return None

def set_option(option, value):
    options[option] = value

def add_to_queue(data, address):
    connection = get_connection(address[0], address[1])
    connection["packets_queue"].append(data)
    if connection["sequence_order"] >= 255:
        connection["sequence_order"] = 0
    else:
        connection["sequence_order"] += 1

def get_last_packet(address):
    connection = get_connection(address[0], address[1])
    queue = connection["packets_queue"]
    if len(queue) > 0:
        return queue[-1]
    else:
        return b""
    
def send_ack_queue(address):
    connection = get_connection(address[0], address[1])
    packets.ack["packets"] = []
    packets.ack["packets"].append(connection["sequence_order"])
    socket.send_buffer(packets.write_ack(), address)
    
def send_encapsulated(data, address, reliability, sequence_order, need_ack = False, reliable_frame_index = 0, sequenced_frame_index = 0, ordered_frame_index = 0, order_channel = 0, compound_size = 0, compound_id = 0, compound_index = 0):
    packets.encapsulated["body"] = data
    packets.encapsulated["flags"] = reliability
    packets.encapsulated["sequence_order"] = sequence_order
    packets.encapsulated["need_ack"] = need_ack
    packets.encapsulated["reliable_frame_index"] = reliable_frame_index
    packets.encapsulated["sequenced_frame_index"] = sequenced_frame_index
    packets.encapsulated["order"]["ordered_frame_index"] = ordered_frame_index
    packets.encapsulated["order"]["order_channel"] = order_channel
    packets.encapsulated["fragment"]["compound_size"] = compound_size
    packets.encapsulated["fragment"]["compound_id"] = compound_id
    packets.encapsulated["fragment"]["index"] = compound_index
    packet = packets.write_encapsulated()
    socket.send_buffer(packet, address)
    if need_ack:
        send_ack_queue(address)
    add_to_queue(packet, address)

def packet_handler(data, address):
    id = data[0]
    connection = get_connection(address[0], address[1])
    if connection != None:
        if id == messages.ID_NACK:
            packets.read_encapsulated(get_last_packet(address))
            packets.encapsulated["flags"] = 0
            packets.encapsulated["sequence_order"] = connection["sequence_order"]
            socket.send_buffer(packets.write_encapsulated(), address)
        elif id == messages.ID_ACK:
            pass
        else:
            packets.read_encapsulated(data)
            data_packet = packets.encapsulated["body"]
            id = data_packet[0]
            print("DATA_PACKET -> " + str(hex(id)))
            if id < 0x80:
                if connection["connecton_state"] == status["connecting"]:
                    if id == messages.ID_CONNECTION_REQUEST:
                        buffer = handler.handle_connection_request(data_packet, connection)
                        send_encapsulated(buffer, address, 0, connection["sequence_order"], True)
                    elif id == messages.ID_NEW_CONNECTION:
                        packets.read_encapsulated(data)
                        packets.read_new_connection(packets.encapsulated["body"])
                        print(packets.new_connection)
                        connection["connecton_state"] = status["connected"]
                        send_ack_queue(address)
                elif id == messages.ID_CONNECTION_CLOSED:
                    connection["connecton_state"] = status["disconnecting"]
                    remove_connection(address[0], address[1])
                    connection["connecton_state"] = status["disconnected"]
                elif id == messages.ID_CONNECTED_PING:
                    buffer = handler.handle_connected_ping(data_packet)
                    send_encapsulated(buffer, address, 0, connection["sequence_order"], True)
            if connection["connecton_state"] == status["connected"]:
                options["custom_handler"](data, address)
    elif id == messages.ID_UNCONNECTED_PING:
        socket.send_buffer(handler.handle_unconnected_ping(data), address)
    elif id == messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS:
        socket.send_buffer(handler.handle_unconnected_ping_open_connections(data), address)
    elif id == messages.ID_OPEN_CONNECTION_REQUEST_1:
        socket.send_buffer(handler.handle_open_connection_request_1(data), address)
    elif id == messages.ID_OPEN_CONNECTION_REQUEST_2:
        socket.send_buffer(handler.handle_open_connection_request_2(data, (address[0], address[1], 4)), address)

def run():
    socket.create_socket((options["ip"], options["port"]))
    while True:
        recv = socket.receive_buffer()
        if recv != None:
            data, addr = recv
            packet_handler(data, addr)
