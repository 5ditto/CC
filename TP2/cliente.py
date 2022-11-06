import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# AF_INET -> IPv4
# SOCK_DGRAM -> UDP

msg = "Adoro Redes :)"

s.sendto(msg.encode('utf-8'), ('127.0.0.1', 12345))