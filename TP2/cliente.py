# Este código implementa o CL
# O primeiro parâmetro é da forma IP[:porta] que representa o IP do servidor DNS a usar como destino das querys
# O segundo parâmetro é o nome completo do parâmetro NAME
# O terceiro parâmetro é o tipo de valor esperado TYPE OF VALUE
# O quarto parâmetro indica se a query deve ser feita de maneira recursiva ou não
import socket
import sys
import re
import random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# AF_INET -> IPv4
# SOCK_DGRAM -> UDP
splited = re.split("\:|\]", sys.argv[1])
splited[0] = splited[0][:-1]
ipServer = splited[0]
porta = splited[1]
name = sys.argv[2]
typeValue = sys.argv[3]
if len(sys.argv) < 5:
    recursiva = False
else:
    recursiva = True

def geraMsgQuery(recursiva, name, typeValue):
    msgId = str(random.randint(1, 65535))
    flags = 'Q'
    if recursiva:
        flags += '+R'
    responseCode = '0'
    nValues = '0'
    nAuthorities = '0'
    nExtraVal = '0'
    return msgId + "," + flags + "," + responseCode + "," + nValues + "," + nAuthorities + "," + nExtraVal + ";" + name + "," + typeValue + ";" 



#print("Ip: " + ipServer + ", porta: " + porta + ", name: " + name + ", tipo do valor: " + typeValue + ", recursivo: " + str(recursiva)) 

msg = geraMsgQuery(recursiva, name, typeValue)
s.sendto(msg.encode('utf-8'), (ipServer, int(porta)))
print(msg)