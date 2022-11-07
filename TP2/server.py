import socket 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# AF_INET -> IPv4
# SOCK_DGRAM -> UDP

endereco = '127.0.0.1'
porta = 12345
s.bind((endereco, porta ))

print(f"Estou à escuta no {endereco}:{porta}") 

while True:
    msg, add = s.recvfrom(1024)
    print(msg.decode('utf-8'))
    print(f"Recebi uma mensagem do cliente {add}")

s.close()