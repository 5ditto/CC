import socket 
from dominio import Dominio

# Primeira coisa que o SS faz é fazer a primeira transferência de zona
# Na transferência de zona o cliente é o SS e o servidor é o SP
# Falta implementar isto na transferência de zona:
# O SS vai verificando se recebeu todas as entradas esperadas até um tempo predefinido se esgotar. Quando esse tempo terminar
# o SS termina a conexão TCP e desiste da transferência de zona. Deve tentar outra vez após um intervalo de tempo igual a SOARETRY. 
def transferenciaZona(dom):
    dbString = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 3333))

        # Primeiro enviar o nome completo do domínio
        msg = dom.name + "."
        s.sendall(msg.encode('utf-8'))
        print("Nome")
        nrEntradas = s.recv(1024) # recebe o número de entradas da db
        print(str(nrEntradas))
        s.sendall(nrEntradas)     # aceita respondendo com o mesmo número que recebeu

        while True:
            parteDb = s.recv(1024).decode('utf-8')
            print("DB")
            if not parteDb:
                print("Acabou")
                return dbString
            dbString += parteDb
            s.close()
    except Exception as ex:
        print("Exception Occurred: %s"%ex)
        s.close()
    
    return dbString

# Antes de fazer a transferência de zona o SS verifica se tem a sua db atualizada ou não
#def verificaVersaoDB(dom):


d = Dominio()
d.parseFicheiroConfig("config.txt")
string = transferenciaZona(d)
print(string)
d.parseStringParaDB(string)
print(str(d.db))
