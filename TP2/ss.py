import socket 
import re
import sys
from dominio import Dominio
from logs import Logs
from cache import Cache

class SS:

    def __init__(self):
        self.cache = Cache()
        self.logs = Logs("SS")
        self.dom = Dominio()
        self.versaoDB = -1
        self.db = dict()
        self.dom.parseFicheiroConfig("config.txt")
        #self.logs.ST(sys.argv[1], sys.argv[2], sys.argv[3])
    
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
            if len(entrada) >= 6:
                self.logs.EV("Registada entrada na cache do SS")
                self.cache.registaAtualizaEntrada(name, entrada[2], entrada[3],  ttl, 'SP', entrada[5])
            else:
                self.logs.EV("Registada entrada na cache do SS")
                self.cache.registaAtualizaEntrada(name, entrada[2], entrada[3],  ttl, 'SP')

    # Na transferência de zona o cliente é o SS e o servidor é o SP
    # Falta implementar isto na transferência de zona:
    # O SS vai verificando se recebeu todas as entradas esperadas até um tempo predefinido se esgotar. Quando esse tempo terminar
    # o SS termina a conexão TCP e desiste da transferência de zona. Deve tentar outra vez após um intervalo de tempo igual a SOARETRY. 
    def transferenciaZona(self, s):
        dbString = ''
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #s.connect(('127.0.0.1', 3333))
        # Primeiro enviar o nome completo do domínio
        msg = self.dom.name + "."
        print("Domínio: " + msg)
        s.sendall(msg.encode('utf-8'))
        nrEntradas = s.recv(1024) # recebe o número de entradas da db
        print(str(nrEntradas))
        s.sendall(nrEntradas) # aceita respondendo com o mesmo número que recebeu
        while True:
            parteDb = s.recv(1024).decode('utf-8')
            if not parteDb:
                # Faz o parse da string final da transferencia de zona para a "cache" do SS
                self.constroiCacheSS(dbString)
                self.logs.ZT(s,"SS"," "," ")
                return dbString
            dbString += parteDb

    # Primeira coisa que o SS faz é verificar se necessita fazer uma transferência de zona
    # Como no inicio a base de dados do SS é vazia ele tem que fazer a transferència de zona
    # Antes de fazer a transferência de zona o SS verifica se tem a sua db atualizada ou não
    def verificaVersaoDB(self):
        dbString = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect(('127.0.0.1', 5555))

            msg = 'VersaoDB'
            s.sendall(msg.encode('utf-8'))

            versao = s.recv(1024).decode('utf-8')
            print(versao)
            if versao != self.versaoDB:# Base de dados do SS está desatualizada
                s.sendall('continua'.encode('utf-8'))
                dbString = self.transferenciaZona(s)
            else:
                s.sendall('termina'.encode('utf-8'))
                s.close()
        except Exception as ex: 
            print("Exception Occurred: %s"%ex)
            s.close()

        return dbString

ss = SS()
ss.verificaVersaoDB()
print(ss.cache.cache)