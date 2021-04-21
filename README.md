# PRakNet
A low level raknet implementation

Installation:

Linux / MacOS ->

```pip3 install praknet```

Windows ->

```pip install praknet```

Usage:

server ->

```
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
        send_packet = {
            "reliability": 0,
            "is_fragmented": False,
            "body": new_packet
        }
        server.send_frame(send_packet, address)
        server.options["entities"] += 1
        connection["entity_id"] = server.options["entities"]
        new_packet = b"\x87\x01\x02\x03\x04\x00\x00\x00\x00\x00\x00\x00\x01" + struct.pack(">l", server.options["entities"]) + encode_pos([0, 4, 0])
        connection["pos"] = [0, 4, 0]
        connection["yaw"] = 0
        connection["pitch"] = 0
        send_packet = {
            "reliability": 0,
            "is_fragmented": False,
            "body": new_packet
        }
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
            send_packet = {
                "reliability": 0,
                "is_fragmented": False,
                "body": new_packet
            }
            server.send_frame(send_packet, address)
    elif identifier == 0x84:
        message = connection["username"] + " joined the game."
        new_packet = b"\x85" + struct.pack(">H", len(message)) + message.encode()
        send_packet = {
            "reliability": 0,
            "is_fragmented": False,
            "body": new_packet
        }
        server.broadcast_frame(send_packet)
        print(message)

server.options["custom_handler"] = custom_handler
server.options["name"] = "MCCPP;MINECON;PRakNet Test MCPI Server"
server.run()
```

client ->

```
from praknet import client
import threading

client.options["ip"] = "0.0.0.0"
client.options["port"] = 19132

def handle(frame):
    if frame["body"][0] == 0x87:
        client.send_reliable(b"\x84\x01")
        client.send_reliable(b'\x94\x00\x00\x00\x01C\x00\x00\x00B\x88\x00\x00C\x00&\xca\x00\x00\x00\x00\x00\x00\x00\x00')

client.options["custom_handler"] = handle

client.connection["state"] = 1

thread = threading.Thread(target = client.packet_handler, args = [])
thread.setDaemon(True)
thread.start()

login = False

while True:
    if client.connection["state"] == 2:
        if login == False:
            client.send_reliable(b"\x82\x00\x07PRakNet\x00\x00\x00\t\x00\x00\x00\t")
            login = True
```
