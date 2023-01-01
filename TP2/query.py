import socket
import re
import random
from dnsMessageBinary import DNSMessageBinary

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
    
    def geraRespQuery(self, dnsMessage1, autoritativo = False): 
        respQuery = ''

        nameDom = self.dom.name + '.'

        all = self.compareDoms(dnsMessage1.dom)

        # Flags:
        flags = ''
        if dnsMessage1.dom == nameDom and autoritativo:
            flags += 'A+'
        if 'R' in dnsMessage1.flags:
            flags += 'R'
            
        respQuery += str(dnsMessage1.messageId) + "," + flags

        extraValues = ''
        # Response Code:
        index = self.cache.procuraEntradaValid(1, dnsMessage1.dom, dnsMessage1.typeValue)
        if index <= self.cache.nrEntradas and index >= 0:
            responseCode = '0'
            respValues = ''
            nrval = 0

            listaIndex = self.cache.todasEntradasValid(1, dnsMessage1.dom, dnsMessage1.typeValue)
            for index in listaIndex:
                respValues += self.cache.entrada(index) + ";"
                nrval += 1
                val = self.cache.campoValor(index)
                comp = val.replace("." + dnsMessage1.dom , "")
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i) + ";"

        elif dnsMessage1.dom == nameDom:
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
        
        subDominio = False
        if self.dom.name in dnsMessage1.dom and self.dom.name + "." != dnsMessage1.dom:
            subDominio = True

        listaIndex = self.cache.todasEntradasValid(1, dnsMessage1.dom, 'NS')
        for index in listaIndex:
            authorities += self.cache.entrada(index) + ";"
            nrAutorithies += 1
            if subDominio: # Query sobre um sub-domínio
                val = self.cache.campoValor(index)
                lista = val.split(".")
                comp = lista[0] + "." + lista[1]
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i) + ";"
            else:
                val = self.cache.campoValor(index)
                comp = val.replace("." + dnsMessage1.dom ,"")
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i) + ";"

        nrAutoridades = str(nrAutorithies)
        nrExtra = nrval + nrAutorithies
        nrExtraValues = str(nrval + nrAutorithies)   
        respQuery += "," + nrAutoridades + "," + nrExtraValues + ";" + dnsMessage1.dom + "," + dnsMessage1.typeValue + ";"
        respQuery += respValues
        if nrAutorithies > 0:
            respQuery += authorities
        if nrval + nrAutorithies > 0 and nrAutorithies > 0:
            respQuery += extraValues 

        dnsMessage2 = DNSMessageBinary(dnsMessage1.messageId, flags, responseCode, nrval, nrAutorithies, nrExtra, dnsMessage1.dom, dnsMessage1.typeValue, respValues, authorities, extraValues)

        return (respQuery, dnsMessage2, all)

    def recebeQuerys(self, autoritativo = False):
        while True:
            bytes, add = self.socketUDP.recvfrom(1024)
            dnsMessage1 = DNSMessageBinary.deconvertMessage(bytes)
            debug = dnsMessage1.dnsMessageDebug(True) # True porque se trata de um pedido de query
            logs = dnsMessage1.dnsMessageLogs(True) # True porque se trata de um pedido de query

            msgResp, dnsMessage2, all = self.geraRespQuery(dnsMessage1, autoritativo)
            self.logs.QR_QE(True, str(add), logs, debug, all)
            bytes = dnsMessage2.convertMessage()
            debug = dnsMessage2.dnsMessageDebug(False) # False porque é a resposta a uma query 
            logs = dnsMessage2.dnsMessageLogs(False) # False porque é a resposta a uma query 

            self.socketUDP.sendto(bytes, add)
            self.logs.RP_RR(False, str(add), logs, debug, all)

    def geraMsgQuery(self):
        msgId = random.randint(1, 65535)
        flags = 'Q'

        if self.recursiva:
            flags += '+R'

        return DNSMessageBinary(msgId,flags,"0",0,0,0,self.name,self.typeValue,"","","")

    def enviaQuery(self):
        dnsMessage1 = self.geraMsgQuery()
        bytes = dnsMessage1.convertMessage()
        self.socketUDP.sendto(bytes, (self.ipServer, int(self.porta)))
        bytes, add = self.socketUDP.recvfrom(1024)
        dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes)
        return (dnsMessage2.dnsMessageDebug(False), add)

    # Cenas do SR
    # Neste método temos que verificar se o SR tem a informação relativa à query na sua Cache
    # Se tiver, o próprio SR responde à query
    # Se não, o SR pede a informação ao servidor autoritativo do domínio em questão
    def recebeQuerysDoCL(self):
        while True:
            bytes, add = self.socketUDP.recvfrom(1024)
            dnsMessage1 = DNSMessageBinary.deconvertMessage(bytes)
            logs = dnsMessage1.dnsMessageLogs(True) # True porque é um pedido de query
            debug = dnsMessage1.dnsMessageDebug(True) # True porque é um pedido de query
            self.logs.QR_QE(True, str(add), logs, debug)

            # All indica se o ficheiro losg a usar é o logs normal ou o logs all
            all = self.compareDoms(dnsMessage1.dom)
            
            index = self.cache.procuraEntradaValid(1, dnsMessage1.dom, dnsMessage1.typeValue)
            if index >= 0 and index <= self.cache.nrEntradas: # Temos a resposta em cache logo é só responder diretamente ao CL
                respString, dnsMessage2, all = self.geraRespQuery(dnsMessage1, False)
                bytes = dnsMessage2.convertMessage()
                logsSV = dnsMessage2.dnsMessageLogs(False) # False porque se trata da resposta a uma query
                debugSV = dnsMessage2.dnsMessageDebug(False) # False porque se trata da resposta a uma query
            else: # A resposta à query não está em cache logo vamos ter que perguntar aos servidores
                if (dnsMessage1.dom in self.dom.endDD.keys()) and len(self.dom.endDD[dnsMessage1.dom]) > 0: # Tenho pelo menos uma entrada DD para aquele dominio
                    splited = re.split(":", self.dom.endDD[dnsMessage1.dom][0])
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(bytes, (splited[0], int(splited[1]))) 
                    self.logs.QR_QE(False, self.dom.endDD[dnsMessage1.dom][0], logs, debug, all)

                    bytes, add2 = s.recvfrom(1024)
                    dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes)
                    logsSV = dnsMessage2.dnsMessageLogs(False) # False porque se trata da resposta a uma query
                    debugSV = dnsMessage2.dnsMessageDebug(False) # False porque se trata da resposta a uma query
                    # respString = resp.decode('utf-8')
                    self.logs.RP_RR(True, str(add2), logsSV, debugSV, all)
                    self.registaRespostaEmCache(dnsMessage2)
                else:
                    # Não existe numa entrada DD sobre o domínio em questão para obter a resposta diretamente, logo vamos perguntar ao ST
                    resposta = False
                    recursiva = False
                    if 'R' in dnsMessage1.flags:
                        recursiva = True
                    
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                    ip, porta = self.dom.endSTs[0]
                    
                    if dnsMessage1.typeValue == 'PTR':
                        # Reverse mapping
                        ip, porta = self.dom.endSTs[2]
                        dnsMessage2 = DNSMessageBinary(random.randint(1, 65535), dnsMessage1.flags, "0", 0, 0, 0, "in-addr.reverse.", dnsMessage1.typeValue, "", "", "")
                        resposta, ip, porta = self.queryAoServer(s, dnsMessage2, ip, porta)
                        
                        if resposta == False: # Se ainda não tivermos a reposta
                            dnsMessage4 = DNSMessageBinary(random.randint(1, 65535), dnsMessage1.flags, "0", 0, 0, 0, "10.in-addr.reverse.", dnsMessage1.typeValue, "", "", "")
                            reposta, ip, porta = self.queryAoServer(s, dnsMessage4, ip, porta)

                    elif dnsMessage1.dom.count('.') == 2: # Significa que a query é sobre um sub-domínio
                        # Temos que primeiro perguntar ao ST a informação sobre os servidores autoritários do domínio principal
                        domDom = dnsMessage1.dom.split(".")[1]
                        domDom += "."
                        dnsMessage2 = DNSMessageBinary(dnsMessage1.messageId, dnsMessage1.flags, dnsMessage1.responseCode, dnsMessage1.nrValues, dnsMessage1.nrAut, dnsMessage1.nrExtra, domDom, dnsMessage1.typeValue, "", "", "")
                        resposta, ip, porta = self.queryAoServer(s, dnsMessage2, ip, porta)
                        
                        if resposta == False: # Se ainda não tivermos a reposta
                            resposta, ip, porta = self.queryAoServer(s, dnsMessage1, ip, porta) # Realiza a query inicial ao SDT
                            
                    else: # Significa que a query é sobre um domínio principal
                        resposta, ip, porta = self.queryAoServer(s, dnsMessage1, ip, porta)

                    if resposta == False: # Ainda não temos a reposta (Vamos fazer a query ao servidor final)
                        # Fazemos a query, depois enviamos a resposta para o cliente
                        s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                        s1.sendto(bytes, (ip, int(porta))) # Envia a query para o server autoritativo do dominio
                        self.logs.QR_QE(False, ip + ":" + porta, logs, debug, all)
    
                        bytes, add2 = s1.recvfrom(1024) # Recebe resposta do server autoritativo do dominio
                        dnsMessageSV = DNSMessageBinary.deconvertMessage(bytes)
                        logsSV = dnsMessageSV.dnsMessageLogs(False) # False porque se trata da resposta a uma query
                        debugSV = dnsMessageSV.dnsMessageDebug(False) # False porque se trata da resposta a uma query
                        self.logs.RP_RR(True, str(add2), logsSV, debugSV, all)
                        self.registaRespostaEmCache(dnsMessageSV)

            # Envia a resposta para o cliente
            self.socketUDP.sendto(bytes, add)
            self.logs.RP_RR(False, str(add), logsSV, debugSV, all)

    # Método do SR
    def ipPortaServerAut(self, extraValues):
        lista = re.split(";", extraValues)

        i = 0
        for elem in lista:
            lista[i] = re.split(" ", elem)
            i += 1

        return re.split(":", lista[0][2])
    
    # Método do SR
    def queryAoServer(self, s, dnsMessage, ip, porta):
        resposta = False

        bytes = dnsMessage.convertMessage()
        logs = dnsMessage.dnsMessageLogs(True) 
        debug = dnsMessage.dnsMessageDebug(True) 
        s.sendto(bytes, (ip, int(porta))) 
        self.logs.QR_QE(False, ip + ":" + porta, logs, debug, all)
        
        bytes2, add2 = s.recvfrom(1024)
        dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes2)
        logs2 = dnsMessage2.dnsMessageLogs(False) # False porque é a resposta a uma query
        debug2 = dnsMessage2.dnsMessageDebug(False) # False porque é a resposta a uma query
        self.logs.RP_RR(True, str(add2), logs2, debug2, all)
        self.registaRespostaEmCache(dnsMessage2)
        if(dnsMessage2.respValues == ""): # O ST não tem a resposta em cache
            ip,porta = self.ipPortaServerAut(dnsMessage2.extraValues)
            print("ipPorta: " + ip + ":" + porta)
        else:
            resposta = True
        
        return (resposta, ip, porta)


    def registaRespostaEmCache(self, dnsMessage):
        index = -1

        aRegistar = dnsMessage.respValues + dnsMessage.autValues + dnsMessage.extraValues
        lista = re.split(';', aRegistar)

        i = 0
        for elem in lista:
            lista[i] = re.split(' ', elem)
            i += 1

        for entrada in lista:
            if len(entrada) > 1:
                if len(entrada) >= 5:
                    index = self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS',entrada[4])
                else:
                    index = self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS')
        
        return index

    def compareDoms(self, dom):
        dominio = self.dom.name + "."

        # Se isto se verificar, que dizer que estamos ainda no mesmo domínio por isso o ficheiro logs vai ser o normal
        if dominio == dom: 
            return False
        # Caso contrário, os logs vai para o ficheiro logs all
        return True 
