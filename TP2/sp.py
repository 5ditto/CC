import sys
import socket 
from dominio import Dominio
from logs import Logs
from cache import Cache
from query import Query
import threading

class SP:

    def __init__(self):
        self.portaAtendimento = sys.argv[2]
        self.timeout = int(sys.argv[3])
        self.dom = Dominio(sys.argv[1]) # O primeiro parâmetro do programa é o seu ficheiro config
        self.dom.parseFicheiroConfig()
        self.dom.parseFicheiroListaST()
        self.logs = Logs(self.dom.ficheiroLogs, self.dom.ficheiroLogsAll, sys.argv[4])
        self.logs.ST(self.portaAtendimento, sys.argv[3], sys.argv[4])
        self.logs.EV('ficheiro de configuração lido')
        self.logs.EV('ficheiro de STs lido')
        self.logs.EV('criado ficheiro de logs')
        self.cache = Cache()
        self.dom.parseDB(self.cache, self.logs, 'SP')
        self.logs.EV('ficheiro de dados lido')
        self.query = Query(True, self.dom, self.cache, self.logs, self.timeout, self.portaAtendimento)
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread(target=self.conexaoTCP, args=()).start() # Thread que vai estar à escuta de novas ligações TCP

    def transferenciaZona(self, connection, address):
        # Na transferência de zona o cliente é o SS e o servidor é o SP
        # Primeiro recebe o nome completo do domínio
        ip, porta = address
        nomeDom = connection.recv(1024).decode('utf-8')
        nome = self.dom.name + "."

        if nomeDom != nome : # Nome de domínio inválido

            self.logs.EZ(ip, str(porta),'SP')
            connection.close()
            return False

        autorizacao = False
        for ipSS in self.dom.endSS:
            # Quem está a pedir a transferência de zona tem permissão para receber uma cópia da base de dados
            if ipSS == ip:
                autorizacao = True
                break

        # Quem está a pedir a transferência de zona não tem permissão para receber uma cópia da base de dados
        if autorizacao == False:
            connection.close()
            self.logs.EZ(ip, str(porta),'SP')
            return False

        nrEntradas = self.cache.nrEntradas
        connection.sendall(str(nrEntradas).encode('utf-8'))
        resposta = connection.recv(1024).decode('utf-8')
        if resposta != str(nrEntradas):
            connection.close()
            self.logs.EZ(ip, str(porta),'SP')
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
        self.logs.ZT(ip, str(porta), 'SP')
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
        porta = 12345
        self.socketTCP.bind(('', int(self.portaAtendimento)))
        self.socketTCP.listen()
        
        while True:
            connection, address = self.socketTCP.accept()
            print(f"Recebi uma ligação do cliente {address}, conexão {connection}")
            threading.Thread(target=self.devolveVersaoDB, args=(connection, address)).start()    

sp = SP()
sp.query.recebeQuerys(True) # True porque se trata de um servidor autoritativo