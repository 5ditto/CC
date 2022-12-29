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
                comp = val.replace("." + nameDom , "")
                print("Comp: " + comp)
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
        listaIndex = self.cache.todasEntradasValid(1, nameDom, 'NS')
        for index in listaIndex:
            authorities += self.cache.entrada(index) + ";"
            nrAutorithies += 1
            val = self.cache.campoValor(index)
            comp = val.replace("." + nameDom ,"")
            print("Comp: " + comp)
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

            # pedido = msg.decode('utf-8')
            # splited1 = re.split(";", pedido)
            # splited2 = re.split(",", splited1[1])
            # splited3 = re.split(",", splited1[0])
            # dom = splited2[0]
            # typeValue = splited2[1] 

            # All indica se o ficheiro losg a usar é o logs normal ou o logs all
            all = self.compareDoms(dnsMessage1.dom)
            
            index = self.cache.procuraEntradaValid(1, dnsMessage1.dom, dnsMessage1.typeValue)
            if index >= 0 and index <= self.cache.nrEntradas: # Temos a resposta em cache logo é só responder diretamente ao CL
                respString, dnsMessage2, all = self.geraRespQuery(dnsMessage1, False)
                bytes = dnsMessage2.convertMessage()
                logsSV = dnsMessage2.dnsMessageLogs(False) # False porque se trata da resposta a uma query
                debugSV = dnsMessage2.dnsMessageDebug(False) # False porque se trata da resposta a uma query
            else: # A resposta à query não está em cache logo vamos ter que perguntar aos servidores
                nameDom = self.dom.name + "."
                if nameDom == dnsMessage1.dom and len(self.dom.endDD) > 0:
                    splited = re.split(":", self.dom.endDD[0])
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(bytes, (splited[0], int(splited[1]))) 
                    self.logs.QR_QE(False, self.dom.endDD[0], logs, debug, all)

                    bytes, add2 = s.recvfrom(1024)
                    dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes)
                    logsSV = dnsMessage2.dnsMessageLogs(False) # False porque se trata da resposta a uma query
                    debugSV = dnsMessage2.dnsMessageDebug(False) # False porque se trata da resposta a uma query
                    # respString = resp.decode('utf-8')
                    self.logs.RP_RR(True, str(add2), logsSV, debugSV, all)
                    self.registaRespostaEmCache(dnsMessage2)
                else:
                    # Não existe numa entrada DD sobre o domínio em questão para obter a resposta diretamente, logo vamos perguntar ao ST
                    recursiva = False
                    if 'R' in dnsMessage1.flags:
                        recursiva = True
                    
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                    ip, porta = self.dom.endSTs[0]
                    
                    if dnsMessage1.typeValue == 'PTR':
                        # Reverse mapping
                       
                        self.query1STSDT("in-addr.reverse.", recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST("in-addr.reverse.", recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')
                        
                        s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.query1STSDT("10.in-addr.reverse.", recursiva, ip, porta, s3, all) # Primeira query ao SP (dom e 'NS')
                        ip, porta = self.query2SDT("10.in-addr.reverse.", recursiva, ip, porta, s3, all) # Segunda query ao SP (nomeServerAut e 'A')

                    elif dnsMessage1.dom.count('.') == 2: # Significa que a query é sobre um sub-domínio
                        # Temos que primeiro perguntar ao ST a informação sobre os servidores autoritários do domínio principal
                        domDom = dnsMessage1.dom.split(".")[1]
                        domDom += "."

                        self.query1STSDT(domDom, recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST(domDom, recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')

                        # Envia query ao SDT para receber a informação sobre os servidor autoritários do seu sub-domínio
                        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.query1STSDT(dnsMessage1.dom, recursiva, ip, porta, s2, all) # Primeira query ao SDT (dom e 'NS')
                        ip, porta = self.query2SDT(dnsMessage1.dom, recursiva, ip, porta, s2, all) # Segunda query ao SDT (nomeServerAut e 'A')

                    else: # Significa que a query é sobre um domínio principal
                        self.query1STSDT(dnsMessage1.dom, recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST(dnsMessage1.dom, recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')

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

    def query1STSDT(self, dom, recursiva, ip, porta, s, all):
        msgId = random.randint(1, 65535)
        flags = 'Q'
        if recursiva:
            flags += '+R'
        
        # queryST = msgId + "," + flags + ",0,0,0,0;" + dom + ",NS;"
        dnsMessage1 = DNSMessageBinary(msgId, flags, "0", 0, 0, 0, dom, "NS", "", "", "")
        bytes1 = dnsMessage1.convertMessage()
        logs1 = dnsMessage1.dnsMessageLogs(True) # True porque se trata de um pedido de uma query
        debug1 = dnsMessage1.dnsMessageDebug(True) # True porque se trata de um pedido de uma query

        s.sendto(bytes1, (ip, int(porta))) # Envia query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, logs1, debug1, all)

        bytes2, add2 = s.recvfrom(1024) # Recebe resposta do ST
        dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes2)
        logs2 = dnsMessage2.dnsMessageLogs(False) # False porque se trata de uma resposta a uma query
        debug2 = dnsMessage2.dnsMessageDebug(False) # False porque se trata de uma resposta a uma query
        self.logs.RP_RR(True, str(add2), logs2, debug2, all)
        self.registaRespostaEmCache(dnsMessage2) # Regista a resposta na cache

    def query2ST(self, dom, recursiva, ip, porta, s, all):
        msgId = random.randint(1, 65535)
        flags = 'Q'
        if recursiva:
            flags += '+R'

        index = self.cache.procuraEntradaValid(1, dom, 'NS')
        if index > -1 and index <= self.cache.nrEntradas:
            nomeAutoritativo = self.cache.cache[index-1][2]
            nomeAut = nomeAutoritativo.replace("." + dom, "")

        # queryST = msgId + "," + flags + ",0,0,0,0;" + nomeAut + ",A;"
        dnsMessage1 = DNSMessageBinary(msgId, flags, "0", 0, 0, 0, nomeAut, "A", "", "", "")
        bytes = dnsMessage1.convertMessage()
        logs1 = dnsMessage1.dnsMessageLogs(True) # True porque se trata de um pedido de uma query
        debug1 = dnsMessage1.dnsMessageDebug(True) # True porque se trata de um pedido de uma query
        s.sendto(bytes, (ip, int(porta))) # Envia a segunda query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, logs1, debug1, all)

        bytes2, add2 = s.recvfrom(1024) # Recebe a segunda resposta do ST
        dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes2)
        logs2 = dnsMessage2.dnsMessageLogs(False) # False porque se trata de uma resposta a uma query
        debug2 = dnsMessage1.dnsMessageDebug(False) # False porque se trata de uma resposta a uma query
        self.logs.RP_RR(True, str(add2), logs2, debug2, all)
        index = self.registaRespostaEmCache(dnsMessage2) # Regista a resposta na cache
        
        ipPortaServer = self.cache.cache[index][2]
        print(ipPortaServer)
        lista = re.split(":", ipPortaServer)
        return (lista[0], lista[1])

    def query2SDT(self, dom, recursiva, ip, porta, s, all):
        msgId = random.randint(1, 65535)
        flags = 'Q'
        if recursiva:
            flags += '+R'

        index = self.cache.procuraEntradaValid(1, dom, 'NS')
        if index > -1 and index <= self.cache.nrEntradas:
            nomeAutoritativo = self.cache.cache[index-1][2]
            lista = nomeAutoritativo.split(".")
            nomeAut = lista[0] + "." + lista[1]
        
        # querySDT = msgId + "," + flags + ",0,0,0,0;" + nomeAut + ",A;"
        dnsMessage1 = DNSMessageBinary(msgId, flags, "0", 0, 0, 0, nomeAut, "A", "", "", "")
        bytes = dnsMessage1.convertMessage()
        logs1 = dnsMessage1.dnsMessageLogs(True) # True porque se trata de um pedido de uma query
        debug1 = dnsMessage1.dnsMessageDebug(True) # True porque se trata de um pedido de uma query
        s.sendto(bytes, (ip, int(porta))) # Envia a segunda query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, logs1, debug1, all)

        bytes2, add2 = s.recvfrom(1024) # Recebe a segunda resposta do ST
        dnsMessage2 = DNSMessageBinary.deconvertMessage(bytes2)
        logs2 = dnsMessage2.dnsMessageLogs(False) # False porque se trata de uma resposta a uma query
        debug2 = dnsMessage2.dnsMessageDebug(False) # False porque se trata de uma resposta a uma query
        self.logs.RP_RR(True, str(add2), logs2, debug2, all)
        self.registaRespostaEmCache(dnsMessage2) # Regista a resposta na cache

        index = self.cache.procuraEntradaValid(1, nomeAut, 'A')
        ipPorta = self.cache.cache[index-1][2]
        lista = re.split(":", ipPorta)
        return (lista[0], lista[1])

    def registaRespostaEmCache(self, dnsMessage):
        index = -1

        aRegistar = dnsMessage.respValues + dnsMessage.autValues + dnsMessage.extraValues
        lista = re.split(';', aRegistar)

        i = 0
        for elem in lista:
            lista[i] = re.split(' ', elem)
            i += 1

        print(lista)

        for entrada in lista:
            if len(entrada) > 1:
                if len(entrada) >= 5:
                    index = self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS',entrada[4])
                else:
                    index = self.cache.registaAtualizaEntrada(entrada[0],entrada[1],entrada[2],entrada[3],'OTHERS')
        
        return index

    def compareDoms(self, dom):
        dominio = self.dom.name + "."

        print("Dominio: " + dominio)
        print("Dom: " + dom)

        # Se isto se verificar, que dizer que estamos ainda no mesmo domínio por isso o ficheiro logs vai ser o normal
        if dominio == dom: 
            return False
        # Caso contrário, os logs vai para o ficheiro logs all
        return True 