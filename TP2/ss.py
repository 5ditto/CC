import socket 
import re
import sys
from dominio import Dominio
from logs import Logs
from cache import Cache
from query import Query
import threading

class SS:

    def __init__(self):
        self.timeout = int(sys.argv[3])
        self.portaAtendimento = sys.argv[2]
        self.dom = Dominio(sys.argv[1]) # O primeiro parâmetro do programa é o ficheiro config
        self.dom.parseFicheiroConfig()
        self.logs = Logs(self.dom.ficheiroLogs, self.dom.ficheiroLogsAll, sys.argv[4])
        self.logs.ST(self.portaAtendimento, sys.argv[3], sys.argv[4])
        self.logs.EV('ficheiro de configuração lido')
        self.logs.EV('criado ficheiro de logs')
        self.cache = Cache()
        self.versaoDB = -1
        self.query = Query(True, self.dom, self.cache, self.logs, self.timeout, self.portaAtendimento)
        # Thread que vai estar sempre à espera de novas querys
        threading.Thread(target = self.query.recebeQuerys, args = ([True])).start()
    
    def encontraNomeTTLDom(self, lista):
        name = ''
        ttl = ''

        for elem in lista:
            if elem[1] == '@' and elem[2] == 'DEFAULT':
                name = elem[3]
            elif elem[1] == 'TTL' and elem[2] == 'DEFAULT':
                ttl = elem[3]

            if name != '' and ttl != '':
                break
        
        return name, ttl

    def constroiCacheSS(self, dbString):
        lista = re.split('\n', dbString)
        i = 0

        for elem in lista:
            lista[i] = re.split(' ', elem)
            i += 1

        name, ttl = self.encontraNomeTTLDom(lista)

        for entrada in lista:
            if entrada[1] != '#' and len(entrada) > 2:
                if len(entrada) >= 6 and '@' in entrada[1]:
                    entrada[1] = entrada[1].replace('@',name)
                    self.cache.registaAtualizaEntrada(entrada[1], entrada[2], entrada[3], ttl, 'SP', entrada[5])
                elif len(entrada) >= 6 and entrada[1] != '@':
                    self.cache.registaAtualizaEntrada(entrada[1], entrada[2], entrada[3], ttl, 'SP', entrada[5])
                elif len(entrada) < 6 and '@' in entrada[1]:
                    entrada[1] = entrada[1].replace('@',name)
                    self.cache.registaAtualizaEntrada(entrada[1], entrada[2], entrada[3], ttl, 'SP')
                else:
                    self.cache.registaAtualizaEntrada(entrada[1], entrada[2], entrada[3], ttl, 'SP')

            self.logs.EV("Registada entrada na cache do SS")


    # Na transferência de zona o cliente é o SS e o servidor é o SP
    # Falta implementar isto na transferência de zona:
    # O SS vai verificando se recebeu todas as entradas esperadas até um tempo predefinido se esgotar. Quando esse tempo terminar
    # o SS termina a conexão TCP e desiste da transferência de zona. Deve tentar outra vez após um intervalo de tempo igual a SOARETRY. 
    def transferenciaZona(self, s):
        dbString = ''

        # Primeiro enviar o nome completo do domínio
        msg = self.dom.name + "."

        s.sendall(msg.encode('utf-8'))
        nrEntradas = s.recv(1024) # recebe o número de entradas da db

        s.sendall(nrEntradas) # aceita respondendo com o mesmo número que recebeu
        while True:
            parteDb = s.recv(1024).decode('utf-8')
            if not parteDb:
                return dbString
            dbString += parteDb

    # Primeira coisa que o SS faz é verificar se necessita fazer uma transferência de zona
    # Como no inicio a base de dados do SS é vazia ele tem que fazer a transferència de zona
    # Antes de fazer a transferência de zona o SS verifica se tem a sua db atualizada ou não
    def verificaVersaoDB(self):
        dbString = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipPorta = re.split(':', self.dom.endSP)
        
        try:
            s.connect((ipPorta[0], int(ipPorta[1])))

            msg = 'VersaoDB'
            s.sendall(msg.encode('utf-8'))

            versao = s.recv(1024).decode('utf-8')

            if int(versao) != self.versaoDB:# Base de dados do SS está desatualizada
                s.sendall('continua'.encode('utf-8'))
                dbString = self.transferenciaZona(s)
                # Faz o parse da string final da transferencia de zona para a "cache" do SS
                self.constroiCacheSS(dbString)
                x = re.split(":", self.dom.endSP)
                self.logs.ZT(x[0], x[1], 'SS')
                self.versaoDB = int(versao)
            else:
                s.sendall('termina'.encode('utf-8'))
                s.close()
        except Exception as ex: 
            print("Exception Occurred: %s"%ex)
            s.close()

        return dbString
            
ss = SS()
ss.verificaVersaoDB() # Inicia o processo da transferência de zona