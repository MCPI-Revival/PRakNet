import socket as s

socket = None

def create_socket(port):
    socket = s.socket(s.AF_INET, s.SOCK_DGRAM, s.SOL_UDP)
    try:
        socket.bind(("0.0.0.0", port))
    except socket.error as e:
        print(f"Failed to bind!")
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
