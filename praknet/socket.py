import socket as s

socket = s.socket(s.AF_INET, s.SOCK_DGRAM, s.IPPROTO_UDP)

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
        return socket.recvfrom(65535)
    except:
        pass
          
def send_buffer(buffer, address):
    return socket.sendto(buffer, address)
     
def close_socket():
    socket.close()
