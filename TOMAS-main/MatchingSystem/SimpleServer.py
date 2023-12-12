import socket
import numpy as np

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.70.18', 5020))
server.listen(1)
P_SG = 5

while True:
    conn, addr = server.accept()
    cmnd = conn.recv(60)  # The default size of the command packet is 4 bytes
    print(np.array(str(cmnd)[2:-1].split(",")))
    Vmeas = np.array(str(cmnd)[2:-1].split(",")).astype(float)
    Pdbm = (Vmeas - 0.9)/0.09 + P_SG - 17.2 #in dBm
    V = 10**((Pdbm-10)/20) #V = [V3,V2,V1,V0]
    print(V)
server.close()
