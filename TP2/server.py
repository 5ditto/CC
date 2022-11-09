# Podemos considerar isto o SP
import re
import socket 
from dominio import Dominio

def geraRespQuery(msgQuery, dom):  
    x = re.split(",|;", msgQuery)
    msgId = x[0]
    flags = x[1]
    if "R" in flags:
        flags = "R+A"
    # Codificar aqui os casos de erro (1, 2 e 3)
    responseCode = '0' # Não houve erros
    dominio = x[6] 
    typeValue = x[7]
    nValues = str(len(dom.db[typeValue]))
    nAuthorities = str(len(dom.db['NS']))  # Verificar isto
    nExtraVal = str(len(dom.db['A']))      # Verificar isto

    returnMsg = msgId + "," + flags + "," + responseCode + "," + nValues + "," + nAuthorities + "," + nExtraVal
    returnMsg += ";" + dominio + "," + typeValue + ";\n"

    for elem in dom.db[typeValue]:
        returnMsg += dominio + " " + typeValue + " " + elem + "\n"
        returnMsg = returnMsg.replace("TTL", dom.db["TTL"]) # Substituir o "TTL" pelo seu respetivo valor 

    for elem in dom.db['NS']:
        returnMsg += dominio + " NS " + elem + "\n"
        returnMsg = returnMsg.replace("TTL", dom.db["TTL"]) # Substituir o "TTL" pelo seu respetivo valor 
    
    #Parte dos servidores autoritários
    for key in dom.db['A'].keys():
        string = dom.db['A'][key].replace("TTL", dom.db["TTL"])
        returnMsg += key + dominio + " " + "A" + string + "\n"
    return returnMsg


def transferenciaZona(s, dom):
    # Primeiro recebe o nome completo do domínio
    nomeDom = s.recv(1024)
    nomeDom = nomeDom.decode('utf-8')

    if nomeDom != dom.name : # Nome de domínio inválido
        # Terminar ligação TCP
        return False
    
    # Verificar se o IP de quem quer a copia da db está na lista do dom.endSS

    nrEntradas = dom.db['nrEntradas']
    s.sendall(str(nrEntradas).encode('utf-8'))
    
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# AF_INET -> IPv4
# SOCK_DGRAM -> UDP

d = Dominio()
d.parseFicheiroConfig("config.txt")
d.parseFicheiroBaseDadosSP()

endereco = '127.0.0.1'
porta = 12345
s.bind((endereco, porta))

print(f"Estou à escuta no {endereco}:{porta}") 

while True:
    msg, add = s.recvfrom(1024)
    msgQuery = msg.decode('utf-8')
    respMsg = geraRespQuery(msgQuery, d)
    print(respMsg)
    s.sendto(respMsg.encode('utf-8'), add)

s.close()