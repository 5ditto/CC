import logging
import re
# Aspetos positivos : data está bem :)

# Tipos de Entradas que existem
#  QR/QE -> end que recebeu/enviou a query + dados relevante da query 
#  RP/RR -> end que recebeu/enviou a resposta da query + dados relevante da resposta da query 
#  ZT -> end da outra pondta da fransferência + SP/SS + (opcional) duração da transferencia + (opcional) total bytes transferidos
#  EV -> End: 127.0.0.1/ localhost/@ + atividade reportada
#  ER -> 
#  EZ -> end da outra porta + SP/SS
#  FL -> End: 127.0.0.1 + informação do erro ocorrido
#  TO -> tipo de Timeout (reposta a uma query/ tentativa de contacto com SP/ iniciar tranferencia de zona)
#  SP -> End: 127.0.0.1 + razão da paragem
#  ST -> End: 127.0.0.1 + porta de atendimento + timeout(milissegundos) + modo de funcionamento(shy/debug)


# O fileLogs serve para registar todos os logs que estejam relacionados com o domínio ao qual o servidor pertence
# O fileLogsAll serve para registar todos os logs que não estejam relacionados com o domínio ao qual o servidor pertence
class Logs:
    # O modo é se estamos a correr um servidor em modo debug ou shy
    # No modo debug, todos os logs também são mandados para o standard output
    def __init__(self, fileLogs = '', fileLogsAll = '', modo = ''):
        fstLine = "# Log File for DNS server/resolver\n"
        self.fileLogs = fileLogs
        self.fileLogsAll = fileLogsAll
        f = open(self.fileLogs, "a")
        f.write(fstLine)
        f.close()
        self.modo = modo

    # Se recebido == true então significa que o componente recebeu uma query, caso contrário foi ele que enviou uma query
    def QR_QE(self, recebido, endereco, infoQuery = ''):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        
        if recebido:
            string = "QR " + endereco + " " + infoQuery
        else:
            string = "QE " + endereco + " " + infoQuery
        
        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def RP_RR(self, recebido, endereco, infoQuery=''):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        
        if recebido:
            string = "RR " + endereco + " " + infoQuery
        else:
            string = "RP " + endereco + " " + infoQuery

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def ZT(self, endereco, role, time='', totalbytes=''):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        
        if time == '' and totalbytes == '':
            string = "ZT " + endereco + " " + role
        else:
            string = endereco + " " + role + " " + time + " " + totalbytes

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def EV(self, eventType, msg=''):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')

        if msg:
            string = "EV 127.0.0.1 " + eventType + " " + msg 
        else:
            string = "EV 127.0.0.1 " + eventType

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def ER(self, endereco):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        string = "ER " + endereco   

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def EZ(self, ip, porta, role):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')

        string = "EZ " + ip + ":" + porta + " " + role

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def FL(self, errorType):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        string = "FL 127.0.0.1 " + errorType

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def TO(self, timeoutType):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        string = "TO " + timeoutType

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def SP(self, reason):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        string = "SP 127.0.0.1 " + reason

        logging.info(string)
        if self.modo == 'debug':
            print(string)

    def ST(self, port, timeout, mode):
        logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
        string = "ST 127.0.0.1 " + port + " " + timeout + " " + mode
        
        logging.info(string)
        if self.modo == 'debug':
            print(string)