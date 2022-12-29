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
    
    def geraRespQuery(self, msgQuery, autoritativo = False): 
        respQuery = ''
        
        lista = re.split(";", msgQuery)
        headerFields = re.split(',', lista[0])
        queryInfo = re.split(',', lista[1])
        respQuery += headerFields[0]

        nameDom = self.dom.name + '.'

        all = self.compareDoms(queryInfo[0])

        # Flags:
        if queryInfo[0] == nameDom and autoritativo:
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
                respValues += self.cache.entrada(index) + ";"
                nrval += 1
                val = self.cache.campoValor(index)
                comp = val.replace("." + nameDom , "")
                print("Comp: " + comp)
                i = self.cache.procuraEntradaValid(1, comp, 'A')
                extraValues += self.cache.entrada(i) + ";"

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
            authorities += self.cache.entrada(index) + ";"
            nrAutorithies += 1
            val = self.cache.campoValor(index)
            comp = val.replace("." + nameDom ,"")
            print("Comp: " + comp)
            i = self.cache.procuraEntradaValid(1, comp, 'A')
            extraValues += self.cache.entrada(i) + ";"

        nrAutoridades = str(nrAutorithies)
        nrExtraValues = str(nrval + nrAutorithies)   
        respQuery += "," + nrAutoridades + "," + nrExtraValues + ";" + lista[1] + ";"
        respQuery += respValues
        if nrAutorithies > 0:
            respQuery += authorities
        if nrval + nrAutorithies > 0 and nrAutorithies > 0:
            respQuery += extraValues 
        return (respQuery, all)

    def recebeQuerys(self, autoritativo = False):
        while True:
            msg, add = self.socketUDP.recvfrom(1024)
            msgString = msg.decode('utf-8')

            msgResp, all = self.geraRespQuery(msgString, autoritativo)
            self.logs.QR_QE(True, str(add), msgString, all)

            self.socketUDP.sendto(msgResp.encode('utf-8'), add)
            self.logs.RP_RR(False, str(add), msgResp, all)

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
            splited3 = re.split(",", splited1[0])
            dom = splited2[0]
            typeValue = splited2[1] 

            # All indica se o ficheiro losg a usar é o logs normal ou o logs all
            all = self.compareDoms(dom)
            
            index = self.cache.procuraEntradaValid(1,dom,typeValue)
            if index >= 0 and index <= self.cache.nrEntradas: # Temos a resposta em cache logo é só responder diretamente ao CL
                respString = self.geraRespQuery(pedido, False)
            else: # A resposta à query não está em cache logo vamos ter que perguntar aos servidores
                nameDom = self.dom.name + "."
                if nameDom == dom and len(self.dom.endDD) > 0:
                    splited = re.split(":", self.dom.endDD[0])
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(msg, (splited[0], int(splited[1]))) 
                    self.logs.QR_QE(False, self.dom.endDD[0], msg.decode('utf-8'), all)
                    resp, add2 = s.recvfrom(1024)
                    respString = resp.decode('utf-8')
                    self.logs.RP_RR(True, str(add2), respString, all)
                    self.registaRespostaEmCache(respString)
                else:
                    # Não existe numa entrada DD sobre o domínio em questão para obter a resposta diretamente, logo vamos perguntar ao ST
                    recursiva = False
                    if 'R' in splited3[1]:
                        recursiva = True
                    
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                    ip, porta = self.dom.endSTs[0]
                    
                    if typeValue == 'PTR':
                        # Reverse mapping
                       
                        self.query1STSDT("in-addr.reverse.", recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST("in-addr.reverse.", recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')
                        
                        s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.query1STSDT("10.in-addr.reverse.", recursiva, ip, porta, s3, all) # Primeira query ao SP (dom e 'NS')
                        ip, porta = self.query2SDT("10.in-addr.reverse.", recursiva, ip, porta, s3, all) # Segunda query ao SP (nomeServerAut e 'A')

                    elif dom.count('.') == 2: # Significa que a query é sobre um sub-domínio
                        # Temos que primeiro perguntar ao ST a informação sobre os servidores autoritários do domínio principal
                        domDom = dom.split(".")[1]
                        domDom += "."

                        self.query1STSDT(domDom, recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST(domDom, recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')

                        # Envia query ao SDT para receber a informação sobre os servidor autoritários do seu sub-domínio
                        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.query1STSDT(dom, recursiva, ip, porta, s2, all) # Primeira query ao SDT (dom e 'NS')
                        ip, porta = self.query2SDT(dom, recursiva, ip, porta, s2, all) # Segunda query ao SDT (nomeServerAut e 'A')

                    else: # Significa que a query é sobre um domínio principal
                        self.query1STSDT(dom, recursiva, ip, porta, s, all) # Primeira query ao ST (dom e 'NS')
                        ip, porta = self.query2ST(dom, recursiva, ip, porta, s, all) # Segunda query ao ST (nomeServerAut e 'A')

                    # Fazemos a query, depois enviamos a resposta para o cliente
                    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                    s1.sendto(msg, (ip, int(porta))) # Envia a query para o server autoritativo do dominio
                    self.logs.QR_QE(False, ip + ":" + porta, pedido, all)
                    resp, add2 = s1.recvfrom(1024) # Recebe resposta do server autoritativo do dominio
                    respString = resp.decode('utf-8')
                    self.logs.RP_RR(True, str(add2), respString, all)
                    self.registaRespostaEmCache(respString)

            # Envia a resposta para o cliente
            self.socketUDP.sendto(respString.encode('utf-8'), add)
            self.logs.RP_RR(False, str(add), resp.decode('utf-8'), all)

    def query1STSDT(self, dom, recursiva, ip, porta, s, all):
        msgId = str(random.randint(1, 65535))
        flags = 'Q'
        if recursiva:
            flags += '+R'
        
        queryST = msgId + "," + flags + ",0,0,0,0;" + dom + ",NS;"

        s.sendto(queryST.encode('utf-8'), (ip, int(porta))) # Envia query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, queryST, all)

        resp, add2 = s.recvfrom(1024) # Recebe resposta do ST
        respString = resp.decode('utf-8')
        self.logs.RP_RR(True, str(add2), respString, all)
        self.registaRespostaEmCache(respString) # Regista a resposta na cache

    def query2ST(self, dom, recursiva, ip, porta, s, all):
        msgId = str(random.randint(1, 65535))
        flags = 'Q'
        if recursiva:
            flags += '+R'

        index = self.cache.procuraEntradaValid(1, dom, 'NS')
        if index > -1 and index <= self.cache.nrEntradas:
            nomeAutoritativo = self.cache.cache[index-1][2]
            nomeAut = nomeAutoritativo.replace("." + dom, "")

        queryST = msgId + "," + flags + ",0,0,0,0;" + nomeAut + ",A;"

        s.sendto(queryST.encode('utf-8'), (ip, int(porta))) # Envia a segunda query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, queryST, all)

        resp, add2 = s.recvfrom(1024) # Recebe a segunda resposta do ST
        respString = resp.decode('utf-8')
        self.logs.RP_RR(True, str(add2), respString, all)
        index = self.registaRespostaEmCache(respString) # Regista a resposta na cache
        
        ipPortaServer = self.cache.cache[index][2]
        print(ipPortaServer)
        lista = re.split(":", ipPortaServer)
        return (lista[0], lista[1])

    def query2SDT(self, dom, recursiva, ip, porta, s, all):
        msgId = str(random.randint(1, 65535))
        flags = 'Q'
        if recursiva:
            flags += '+R'

        index = self.cache.procuraEntradaValid(1, dom, 'NS')
        if index > -1 and index <= self.cache.nrEntradas:
            nomeAutoritativo = self.cache.cache[index-1][2]
            lista = nomeAutoritativo.split(".")
            nomeAut = lista[0] + "." + lista[1]
        
        querySDT = msgId + "," + flags + ",0,0,0,0;" + nomeAut + ",A;"

        s.sendto(querySDT.encode('utf-8'), (ip, int(porta))) # Envia a segunda query ao ST
        self.logs.QR_QE(False, ip + ":" + porta, querySDT, all)

        resp, add2 = s.recvfrom(1024) # Recebe a segunda resposta do ST
        respString = resp.decode('utf-8')
        self.logs.RP_RR(True, str(add2), respString, all)
        self.registaRespostaEmCache(respString) # Regista a resposta na cache

        index = self.cache.procuraEntradaValid(1, nomeAut, 'A')
        ipPorta = self.cache.cache[index-1][2]
        lista = re.split(":", ipPorta)
        return (lista[0], lista[1])


    def serverAutoritario(self, dom):
        index = self.cache.procuraEntradaValid(1, dom, 'NS')
        nome = self.cache.cache[index-1][2]
        nome2 = nome.replace("." + dom, "")
        print("Nome: " + nome2)
        index = self.cache.procuraEntradaValid(1, nome2, 'A')
        ipPortaServer = self.cache.cache[index-1][2]
        print("ipPortaServer: " + ipPortaServer)
        lista = re.split(":", ipPortaServer)
        return (lista[0], lista[1])

    def registaRespostaEmCache(self, respQuery):
        index = -1
        lista = re.split(';', respQuery)
        
        i = 0
        for elem in lista:
            lista[i] = re.split(' ', elem)
            i += 1

        # Retira o cabeçalho da query
        lista.pop(0)
        lista.pop(0)
        lista.pop(len(lista)-1)

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