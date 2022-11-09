import re
import socket 
from dominio import Dominio
import time
# Primeira coisa que o SS faz é fazer a primeira transferência de zona
# Na transferência de zona o cliente é o SS e o servidor é o SP
def transferenciaZona(dom):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 3333))

    # Primeiro enviar o nome completo do domínio
    msg = dom.name + "."
    s.sendall(msg.encode('utf-8'))

    nrEntradas = s.recv(1024) # recebe o número de entradas da db
    s.sendall(nrEntradas)     # aceita respondendo com o mesmo número que recebeu

    dbString = ''
    while True:
        msg = s.recv(1024).decode('utf-8')
        print("DB")
        if not msg:
            print("Acabou")
            return dbString
        dbString += msg


d = Dominio()
d.parseFicheiroConfig("config.txt")

string = transferenciaZona(d)
print(string)
