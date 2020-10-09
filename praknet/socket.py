import socket as s

socket = None
    
@staticmethod
def create_socket(port):
    socket = s.socket(s.AF_INET, s.SOCK_DGRAM, s.SOL_UDP)
    try:
        socket.bind(("0.0.0.0", port))
    except socket.error as e:
        print(f"Failed to bind!")
        print(str(e))
    else:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
       
def receiveBuffer():
    try:
        data = socket.recvfrom(65535, 0)
        print(f"IN -> {data}")
        return data
    except:
        pass
          
def sendBuffer(buffer, address):
    data = socket.sendto(buffer, address)
    print(f"OUT -> {data}")
    return data
     
def closeSocket():
    socket.close()
