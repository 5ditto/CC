import socket
import re
import random

class Query:

    # O boolean server indica se a componente se trata de um servidor ou um cliente
    def __init__(self, server, dom = None, cache = None, logs = None, portaAtendimento = None, ipServer = None
    , porta = None, recursiva = None, name = None, typeValue = None):
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
