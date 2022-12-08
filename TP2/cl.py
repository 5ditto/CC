# Este código implementa o CL
# O primeiro parâmetro é da forma IP[:porta] que representa o IP do servidor DNS a usar como destino das querys
# O segundo parâmetro é o nome completo do parâmetro NAME
# O terceiro parâmetro é o tipo de valor esperado TYPE OF VALUE
# O quarto parâmetro indica se a query deve ser feita de maneira recursiva ou não
import sys
import re
import random
from query import Query

class CL:

    def __init__(self):
        splited = re.split(":", sys.argv[1])

        if len(sys.argv) < 5:
            recursiva = False
        else:
            recursiva = True

        self.query = Query(False, ipServer = splited[0], porta = splited[1], recursiva = recursiva, name = sys.argv[2], typeValue = sys.argv[3])

cl = CL()
respMsg, add = cl.query.enviaQuery()
print(respMsg.decode('utf-8'))


#def geraMsgQuery(self):
#    msgId = str(random.randint(1, 65535))
#    flags = 'Q'
#    if self.recursiva:
#        flags += '+R'
#    return msgId + "," + flags + "," + "0,0,0,0" + ";" + self.name + "," + self.typeValue + ";" 

#def queryCL(self):
#    msg = self.geraMsgQuery()
#    self.sUDP.sendto(msg.encode('utf-8'), (self.ipServer, int(self.porta)))
#    RespMsg, add = self.sUDP.recvfrom(1024)
#    print(str(RespMsg))