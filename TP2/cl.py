# Este código implementa o CL
# O primeiro parâmetro é da forma IP[:porta] que representa o IP do servidor DNS a usar como destino das querys
# O segundo parâmetro é o nome completo do parâmetro NAME
# O terceiro parâmetro é o tipo de valor esperado TYPE OF VALUE
# O quarto parâmetro indica se a query deve ser feita de maneira recursiva ou não
import socket
import sys
import re
import random

class CL:

    def __init__(self):
        self.sUDp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        splited = re.split(":", sys.argv[1])
        self.ipServer = splited[0]
        self.porta = splited[1]
        self.name = sys.argv[2]
        self.typeValue = sys.argv[3]
        if len(sys.argv) < 5:
            self.recursiva = False
        else:
            self.recursiva = True

    def geraMsgQuery(self):
        msgId = str(random.randint(1, 65535))
        flags = 'Q'
        if self.recursiva:
            flags += '+R'
        return msgId + "," + flags + "," + "0,0,0,0" + ";" + self.name + "," + self.typeValue + ";" 

    def queryCL(self):
        msg = self.geraMsgQuery()
        self.sUDp.sendto(msg.encode('utf-8'), (self.ipServer, int(self.porta)))
        RespMsg, add = self.sUDp.recvfrom(1024)
        print(str(RespMsg))

cl = CL()
cl.queryCL()