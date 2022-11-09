import re
import socket 
from dominio import Dominio
import time
# Primeira coisa que o SS faz é fazer a transferência de zona

def transferenciaZona(socket, dom):
    # Primeiro enviar o nome completo do domínio
    msg = dom.name + "."
    s.sendall(msg.encode('utf-8'))

    nrEntradas = s.recv(1024) # recebe o número de entradas da db
    s.sendall(nrEntradas)     # aceita respondendo com o mesmo número que recebeu


d = Dominio()
d.parseFicheiroConfig("config.txt")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((d.endSP, 3333))

transferenciaZona(s, d)

while True:
    s.sendall(msg.encode('utf-8'))
    time.sleep(1)
    
s.close()