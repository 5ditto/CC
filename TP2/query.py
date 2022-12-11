import socket
import re
import random

class Query:

    # O boolean server indica se a componente se trata de um servidor ou um cliente
    def __init__(self, server, dom = None, cache = None, logs = None, portaAtendimento = None, 
    ipServer = None, porta = None, recursiva = None, name = None, typeValue = None):
        self.server = server
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Se for um servidor fazemos o bind
        if self.server:
            self.dom = dom
            self.cache = cache
            self.logs = logs
            self.socketUDP.bind(('', int(portaAtendimento)))
        else:
            self.ipServer = ipServer
            self.porta = porta
            self.recursiva = recursiva
            self.name = name
            self.typeValue = typeValue
    
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
            i = self.cache.procuraEntradaValid(1, comp, 'A')
            extraValues += self.cache.entrada(i)[:-1] + ";"

        nrAutoridades = str(nrAutorithies)
        nrExtraValues = str(nrval + nrAutorithies)   
        respQuery += "," + nrAutoridades + "," + nrExtraValues + ";" + lista[1] + "; "
        respQuery += respValues
        respQuery += authorities
        respQuery += extraValues 
        return respQuery

    def recebeQuerys(self):
        while True:
            msg, add = self.socketUDP.recvfrom(1024)
            self.logs.QR_QE(True, str(add), msg.decode('utf-8'))
            msgResp = self.geraRespQuery(msg.decode('utf-8'))
            self.socketUDP.sendto(msgResp.encode('utf-8'), add)
            self.logs.RP_RR(False, str(add), msgResp)

    def geraMsgQuery(self):
        msgId = str(random.randint(1, 65535))
        flags = 'Q'
        if self.recursiva:
            flags += '+R'
        return msgId + "," + flags + "," + "0,0,0,0" + ";" + self.name + "," + self.typeValue + ";" 

    def enviaQuery(self):
        msg = self.geraMsgQuery()
        self.socketUDP.sendto(msg.encode('utf-8'), (self.ipServer, int(self.porta)))
        respMsg, add = self.socketUDP.recvfrom(1024)
        return (respMsg, add)

    # Cenas do SR

    # Neste método temos que verificar se o SR tem a informação relativa à query na sua Cache
    # Se tiver, o próprio SR responde à query
    # Se não, o SR pede a informação ao servidor autoritativo do domínio em questão
    def recebeQuerysDoCL(self):
        while True:
            msg, add = self.socketUDP.recvfrom(1024)
            self.logs.QR_QE(True, str(add), msg.decode('utf-8'))

            pedido = msg.decode('utf-8')
            splited1 = re.split(";", pedido)
            splited2 = re.split(",", splited1[1])
            dom = splited2[0]
            typeValue = splited2[1] 
            
            index = self.cache.procuraEntradaValid(1,dom,typeValue)
            if index >= 0 and index <= self.cache.nrEntradas: # Temos a resposta em cache logo é só responder diretamente ao CL
                respString = self.geraRespQuery(pedido)
            else: # A resposta à query não está em cache logo vamos ter que perguntar aos servidores
                nameDom = self.dom.name + "."
                if nameDom == dom and len(self.dom.endDD) > 0:
                    splited = re.split(":", self.dom.endDD[0])

                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(msg, (splited[0], int(splited[1]))) 
                    self.logs.QR_QE(False, self.dom.endDD[0], msg.decode('utf-8'))
                    resp, add2 = s.recvfrom(1024)
                    respString = resp.decode('utf-8')
                    self.logs.RP_RR(True, str(add2), respString)
                    self.registaRespostaEmCache(respString)
                else:
                    # Não existe numa entrada DD sobre o domínio em questão para obter a resposta diretamente, logo vamos perguntar ao ST
                    return "Ainda não implementado"
            
            self.socketUDP.sendto(respString.encode('utf-8'), add)
            self.logs.RP_RR(False, str(add), resp.decode('utf-8'))

    def registaRespostaEmCache(self, respQuery):
        lista = re.split('\n', respQuery)
        i = 0

        for elem in lista:
            lista[i] = re.split(' ', elem)
            i += 1

        for entrada in lista:
            if len(entrada) >= 5:
                self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS',entrada[4])
            else:
                self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS')