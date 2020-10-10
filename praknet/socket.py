import socket as s

socket = s.socket(s.AF_INET, s.SOCK_DGRAM, s.SOL_UDP)

def create_socket(address):
    try:
        socket.bind(address)
    except s.error as e:
        print("Failed to bind!")
        print(str(e))
    else:
        socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        socket.setsockopt(s.SOL_SOCKET, s.SO_BROADCAST, 1)
       
def receive_buffer():
    try:
        data = socket.recvfrom(65535, 0)
        print(f"IN -> {data}")
        return data
    except:
        pass
          
def send_buffer(buffer, address):
    data = socket.sendto(buffer, address)
    print(f"OUT -> {data}")
    return data
     
def closeSocket():
    socket.close()
