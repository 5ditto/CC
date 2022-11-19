import re
import sys
import socket 
from dominio import Dominio
from logs import Logs
from cache import Cache
import threading

class SP:

    def __init__(self):
        self.dom = Dominio(sys.argv[1]) # O primeiro parâmetro do programa é o seu ficheiro config
        self.dom.parseFicheiroConfig()
        self.dom.parseFicheiroListaST()
        self.logs = Logs(self.dom.ficheiroLogs, self.dom.ficheiroLogsAll)
        self.logs.ST(sys.argv[2], sys.argv[3], sys.argv[4])
        self.logs.EV('ficheiro de configuração lido')
        self.logs.EV('ficheiro de STs lido')
        self.logs.EV('criado ficheiro de logs')
        self.cache = Cache()
        self.parseDB()
        self.logs.EV('ficheiro de dados lido')
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketUDP.bind(("127.0.0.1",12345))
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread(target=self.conexaoTCP, args=()).start() # Thread que vai estar à escuta de novas ligações TCP

    def geraRespQuery(self, msgQuery): 
        respQuery = ''
        
        lista = re.split(";", msgQuery)
        headerFields = re.split(',', lista[0])
        queryInfo = re.split(',', lista[1])
        respQuery += headerFields[0]

        nameDom = self.dom.name + '.'
        print("Nome Domínio: " + nameDom)
        # Flags:
        # Como se trata do SP do domínio em questão então é autoritativo
        if queryInfo[0] == nameDom:
            headerFields[1] += '+A'
            
        # Response Code:
        print(queryInfo)
        index = self.cache.procuraEntradaValid(1, queryInfo[0], queryInfo[1])
        print("Index: "+ str(index))
        if index < self.cache.nrEntradas and index >= 0:
            extraValues = ''
            responseCode = '0'
            respQuery += "," + responseCode
            respValues = ''
            nrval = 0

            listaIndex = self.cache.todasEntradasValid(1, queryInfo[0], queryInfo[1])
            for index in listaIndex:
                respValues += self.cache.entrada(index)
                nrval += 1
                comp = self.cache.campoValor(index)
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i)
            nrValues = str(nrval)

            respQuery += "," + nrValues

        elif queryInfo[0] == nameDom:
            responseCode = '1'
            nrval = 0
            respValues = ''
        else:
            responseCode = '2'
            nrval = 0 
            respValues = ''

        authorities = ''
        nrAutorithies = 0
        listaIndex = self.cache.todasEntradasValid(1, queryInfo[0], 'NS')
        for index in listaIndex:
            authorities += self.cache.entrada(index)
            nrAutorithies += 1
            comp = self.cache.campoValor(index)
            i = self.cache.procuraEntradaValid(1, comp, 'A')
            extraValues += self.cache.entrada(i)
        nrAutoridades = str(nrAutorithies)
        nrExtraValues = str(nrval + nrAutorithies)   
        respQuery += "," + nrAutoridades + "," + nrExtraValues + ";" + lista[1] + "; "
        respQuery += respValues
        respQuery += authorities
        respQuery += extraValues 
        print(respQuery)
        return respQuery

    def recebeQuerys(self):
        msg, add = self.socketUDP.recvfrom(1024)
        self.logs.QR_QE(true, add, msg.decode('utf-8'))
        msgResp = self.geraRespQuery(msg.decode('utf-8'))
        self.socketUDP.sendto(msgResp.encode('utf-8'), add)
        self.logs.RP_RR(false, add, msgResp)

    def transferenciaZona(self, connection, address):
        # Na transferência de zona o cliente é o SS e o servidor é o SP
        # Primeiro recebe o nome completo do domínio
        address = "193.123.5.189" # Isto é só para puder testar (mais tarde vai sair)
        nomeDom = connection.recv(1024).decode('utf-8')
        print("Nome: " + nomeDom)
        nome = self.dom.name + "."

        if nomeDom != nome : # Nome de domínio inválido
            print("Dominio inválido")
            self.logs.EZ(address,'SP')
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
            self.logs.EZ(address,'SP')
            return False

        nrEntradas = self.cache.nrEntradas
        connection.sendall(str(nrEntradas).encode('utf-8'))
        resposta = connection.recv(1024).decode('utf-8')
        if resposta != str(nrEntradas):
            print("Número de entradas não foi aceite")
            connection.close()
            self.logs.EZ(address,'SP')
            return False

        # Mandar cada linha da base de dados para o SS
        f = open(self.dom.ficheiroDb, 'r')
        i = 1       
        respostaDb = ''
        for line in f:
            respostaDb += str(i) + " " + line
            i += 1
        f.close()
        reposta = respostaDb.encode('utf-8')
        self.logs.ZT(address,'SP')
        connection.sendall(reposta)
        connection.close()

    def devolveVersaoDB(self, connection, address):

        msg = connection.recv(1024).decode('utf-8')
        if msg == 'VersaoDB':
            name = self.dom.name + '.'
            index = self.cache.procuraEntradaValid(1, name, 'SOASERIAL')
            connection.sendall(self.cache.cache[index][2].encode('utf-8'))
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
        
    def encontraNomeTTLDom(self, file):
        name = ''
        ttl = ''

        for line in file:
            x = re.split(" ", line)
            if x[1] == 'DEFAULT' and x[0] == '@': 
                name = x[2]
            
            if x[1] == 'DEFAULT' and x[0] == 'TTL':
                ttl = x[2][:-1]

            if name != '' and ttl != '':
                return name, ttl 
        
        return name, ttl
        
    def parseDB(self):
        f = open(self.dom.ficheiroDb, 'r')
        name, ttl = self.encontraNomeTTLDom(f)
        name = name[:-1]
        for line in f:
            splited = re.split(' ', line[:-1]) 
            if splited[0] != '#':
                if len(splited) >= 5:
                    self.cache.registaAtualizaEntrada(name, splited[1], splited[2], ttl, 'FILE', splited[4])
                else:
                    self.cache.registaAtualizaEntrada(name, splited[1], splited[2], ttl, 'FILE')
        
        f.close()

sp = SP()
print(sp.dom)