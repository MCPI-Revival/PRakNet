from praknet import packets
from praknet import server
import struct

def encode_pos(pos):
    return struct.pack(">f", 128 + pos[0]) + struct.pack(">f", 64 + pos[1]) + struct.pack(">f", 128 + pos[2])

def decode_pos(pos):
    return [struct.unpack(">f", pos[:4])[0] - 128, struct.unpack(">f", pos[4:8])[0] - 64, struct.unpack(">f", pos[8:12])[0] - 128]

def custom_handler(data, address):
    if not "entities" in server.options:
        server.set_option("entities", 0)
    connection = server.get_connection(address[0], address[1])
    packets.read_encapsulated(data)
    packet = packets.encapsulated
    id = packet["body"][0]
    if id == 0x82:
        new_packet = b"\x83\x00\x00\x00\x00"
        server.send_encapsulated(new_packet, address, 0, connection["sequence_order"], True)
        server.options["entities"] += 1
        new_packet = b"\x87\x01\x02\x03\x04\x00\x00\x00\x00\x00\x00\x00\x01" + struct.pack(">l", server.options["entities"]) + encode_pos([0, 4, 0])
        server.send_encapsulated(new_packet, address, 0, connection["sequence_order"], True)
    elif id == 0x94:
        server.send_ack_queue(address)
    elif id == 0x84:
        server.send_ack_queue(address)
        player = f"{address[0]}:{address[1]}"
        message = f"{player} joined the game."
        new_packet = b"\x85" + struct.pack(">H", len(message)) + message.encode()
        server.broadcast_encapsulated(new_packet, 0, connection["sequence_order"], True)
        
server.set_option("custom_handler", custom_handler)
server.set_option("name", "MCCPP;MINECON;PRakNet Server")
server.run()
