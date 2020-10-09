from praknet import packets

@staticmethod
def handle_unconnected_ping(data):
    packets.read_unconnected_ping(data)
    packets.unconnected_pong["time"] = packets.unconnected_ping["time"]
    packets.unconnected_pong["server_guid"] = 12345678
    packets.unconnected_pong["magic"] = packets.unconnected_ping["magic"]
    packets.unconnected_pong["data"] = "MCPE;Dedicated Server;390;1.14.60;0;10;13253860892328930865;Bedrock level;Survival;1;19132;19133;"
    data = packet.write_unconnected_pong()
