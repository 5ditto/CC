import re
import sys
from dominio import Dominio
from logs import Logs
from cache import Cache
import socket

class SR:

    def __init__(self):
        self.portaAtendimento = sys.argv[2]
        self.dom = Dominio(sys.argv[1]) # O primeiro parâmetro do programa é o seu ficheiro config
        self.dom.parseFicheiroConfig()
        self.dom.parseFicheiroListaST()
        self.logs = Logs(self.dom.ficheiroLogs, self.dom.ficheiroLogsAll, sys.argv[4])
        self.logs.ST(self.portaAtendimento, sys.argv[3], sys.argv[4])
        self.logs.EV('ficheiro de configuração lido')
        self.logs.EV('ficheiro de STs lido')
        self.logs.EV('criado ficheiro de logs')
        self.cache = Cache()
        self.logs.EV('cache iniciada')
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketUDP.bind(('', int(self.portaAtendimento)))
    

    # Neste método temos que verificar se o SR tem a informação relativa à query na sua Cache
    # Se tiver, o próprio SR responde à query
    # Se não, o SR pede a informação ao servidor autoritativo do domínio em questão
    def recebeQuerysDoCL(self):
        while True:
            msg, add = self.socketUDP.recvfrom(1024)
            self.logs.QR_QE(True, str(add), msg.decode('utf-8'))

            pedido = msg.decode('utf-8')
            splited1 = re.split(pedido, ";")
            splited2 = re.split(splited1[1], ",")
            dom = splited2[0]
            typeValue = splited2[1]
            
            index = self.cache.procuraEntradaValid(1,dom,typeValue)
            if index >= 0 and index <= self.cache.nrEntradas: # Temos a resposta em cache logo é só responder diretamente ao CL
                resp = self.geraRespQuery(pedido)
            else:  # A resposta à query não está em cache logo vamos ter que perguntar aos servidores
                if self.dom.name == dom and len(self.dom.endDD) > 0:
                    splited = re.split(self.dom.endDD, ":")

                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(msg, (splited[0], int(splited[1]))) 
                    msg2, add2 = s.recvfrom(1024)
                    # Ao receber a resposta do servidor o SR tem que registar a resposta em Cache antes de a enviar para o CL
                    self.cache.registaAtualizaEntrada()
                    resp = msg2.decode('utf-8')

            self.socketUDP.sendto(resp.enconde('utf-8'), add)

    def geraRespQuery(self, msgQuery): 
        respQuery = ''
        
        lista = re.split(";", msgQuery)
        headerFields = re.split(',', lista[0])
        queryInfo = re.split(',', lista[1])
        respQuery += headerFields[0]

        nameDom = self.dom.name + '.'

        # Flags:
        # Como se trata do SP do domínio em questão então é autoritativo
        if queryInfo[0] == nameDom:
            headerFields[1] += '+A'
            
        extraValues = ''
        # Response Code:
        index = self.cache.procuraEntradaValid(1, queryInfo[0], queryInfo[1])
        if index <= self.cache.nrEntradas and index >= 0:
            responseCode = '0'
            respValues = ''
            nrval = 0

            listaIndex = self.cache.todasEntradasValid(1, queryInfo[0], queryInfo[1])
            for index in listaIndex:
                respValues += self.cache.entrada(index)[:-1] + ";"
                nrval += 1
                val = self.cache.campoValor(index)
                comp = val.replace(self.dom.name ,"")[:-2]
                print("Comp: " + comp)
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i)[:-1] + ";"

        elif queryInfo[0] == nameDom:
            responseCode = '1'
            nrval = 0
            respValues = ''
        else:
            responseCode = '2'
            nrval = 0 
            respValues = ''

        nrValues = str(nrval)
        respQuery += "," + responseCode + "," + nrValues
        authorities = ''
        nrAutorithies = 0
        listaIndex = self.cache.todasEntradasValid(1, nameDom, 'NS')
        for index in listaIndex:
            authorities += self.cache.entrada(index)[:-1] + ";"
            nrAutorithies += 1
            val = self.cache.campoValor(index)
            comp = val.replace(self.dom.name ,"")[:-2]
            print("Comp: " + comp)
            i = self.cache.procuraEntradaValid(1, comp, 'A')
            extraValues += self.cache.entrada(i)[:-1] + ";"
        nrAutoridades = str(nrAutorithies)
        nrExtraValues = str(nrval + nrAutorithies)   
        respQuery += "," + nrAutoridades + "," + nrExtraValues + ";" + lista[1] + "; "
        respQuery += respValues
        respQuery += authorities
        respQuery += extraValues 
        return respQuery
        
