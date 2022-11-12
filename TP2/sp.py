# Podemos considerar isto o SP
import re
import sys
import socket 
from dominio import Dominio
from logs import Logs
import threading

class SP:

    def __init__(self):
        self.logs = Logs("SP")
        self.dom = Dominio()
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dom.parseFicheiroConfig("config.txt")
        self.dom.parseFicheiroBaseDados()
        self.logs.ST(sys.argv[1], sys.argv[2], sys.argv[3])
        threading.Thread(target=self.conexaoTCP, args=()).start() # Thread que vai estar à escuta de novas ligações TCP


    def geraRespQuery(self, msgQuery, dom):  
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

    def transferenciaZona(self, connection, address):
        # Na transferência de zona o cliente é o SS e o servidor é o SP
        # Primeiro recebe o nome completo do domínio
        address = "193.123.5.189" # Isto é só para puder testar (mais tarde vai sair)
        nomeDom = connection.recv(1024).decode('utf-8')
        print("Nome: " + nomeDom)
        nome = self.dom.name + "."

        if nomeDom != nome : # Nome de domínio inválido
            print("Dominio inválido")
            connection.close()
            return False

        autorizacao = False
        for ip in self.dom.endSS:
            # Quem está a pedir a transferência de zona tem permissão para receber uma cópia da base de dados
            if ip == address:
                autorizacao = True
                break
            
        # Quem está a pedir a transferência de zona não tem permissão para receber uma cópia da base de dados
        if autorizacao == False:
            print("Não tem autorização")
            connection.close()
            return False

        nrEntradas = self.dom.db['nrEntradas']
        connection.sendall(str(nrEntradas).encode('utf-8'))
        resposta = connection.recv(1024).decode('utf-8')
        if resposta != str(nrEntradas):
            print("Número de entradas não foi aceite")
            connection.close()
            return False

        # Mandar cada linha da base de dados para o SS
        f = open(self.dom.ficheiroDb, 'r')
        i = 1
        respostaDb = ''
        for line in f:
            respostaDb += str(i) + " " + line
            i += 1
        f.close()

        connection.sendall(respostaDb.encode('utf-8'))
        connection.close()

    def devolveVersaoDB(self, connection, address):

        msg = connection.recv(1024).decode('utf-8')
        if msg == 'VersaoDB':
            connection.sendall(self.dom.db['SOASERIAL'].encode('utf-8'))
            resposta = connection.recv(1024).decode('utf-8')
            if resposta == 'continua':
                self.transferenciaZona(connection, address)
            elif resposta == 'termina': 
                connection.close()

    # Função que espera por novas ligações TCP ao SP e depois chama a função transferênciaZona para as tratar
    def conexaoTCP(self):
        endereco = '127.0.0.1'
        porta = 5555
        self.socketTCP.bind((endereco, porta))
        self.socketTCP.listen()
        
        while True:
            connection, address = self.socketTCP.accept()
            print(f"Recebi uma ligação do cliente {address}, conexão {connection}")
            threading.Thread(target=self.devolveVersaoDB, args=(connection, address)).start()    


sp = SP()
sp.conexaoTCP()

#endereco = '127.0.0.1'
#porta = 12345
#sUDP.bind((endereco, porta))
#
#
#print(f"Estou à escuta no {endereco}:{porta}") 
#
#while True:
#    msg, add = sUDP.recvfrom(1024)
#    msgQuery = msg.decode('utf-8')
#    respMsg = geraRespQuery(msgQuery, d)
#    print(respMsg)
#    sUDP.sendto(respMsg.encode('utf-8'), add)
#
#s.close()