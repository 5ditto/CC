import logging

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
    def __init__(self, fileLogs = '', fileLogsAll = '', modo = '', st = False):
        fstLine = "# Log File for DNS server/resolver\n"
        self.fileLogs = fileLogs
        self.fileLogsAll = fileLogsAll

        if fileLogs != '':
            f = open(self.fileLogs, "a")
            f.write(fstLine)
            f.close()

        if fileLogsAll != '':
            print("Caminho do logsAll: " + self.fileLogsAll)
            fAll = open(self.fileLogsAll, "a")
            fAll.write(fstLine)
            fAll.close()
        
        if st:
            self.st = True
        else:
            self.st = False

        self.modo = modo

    # Se recebido == true então significa que o componente recebeu uma query, caso contrário foi ele que enviou uma query
    # O último argumento "all" representa se o logs vai para o logsAll ou para o normal
    def QR_QE(self, recebido, endereco, infoQuery = '', all = False):
        
        if recebido:
            string = "QR " + endereco + " " + infoQuery
        else:
            string = "QE " + endereco + " " + infoQuery
        
        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                print("ALL!")
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            
        if self.modo == 'debug':
            print(string)

    def RP_RR(self, recebido, endereco, infoQuery='', all = False):

        if recebido:
            string = "RR " + endereco + " " + infoQuery
        else:
            string = "RP " + endereco + " " + infoQuery

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)

        if self.modo == 'debug':
            print(string)

    def ZT(self, ip, porta, role = '', time = '', totalbytes = '', all = False):
        
        if time == '' and totalbytes == '':
            string = "ZT " + ip + ":" + porta + " " + role
        else:
            string = "ZT " + ip + ":" + porta + " " + role + " " + time + " " + totalbytes

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)

        if self.modo == 'debug':
            print(string)

    def EV(self, eventType, msg='', all = False):

        if msg:
            string = "EV 127.0.0.1 " + eventType + " " + msg 
        else:
            string = "EV 127.0.0.1 " + eventType

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)

        if self.modo == 'debug':
            print(string)

    def ER(self, endereco, all = False):
        string = "ER " + endereco   

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)

        if self.modo == 'debug':
            print(string)

    def EZ(self, ip, porta, role, all = False):

        string = "EZ " + ip + ":" + porta + " " + role

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
        
        if self.modo == 'debug':
            print(string)

    def FL(self, errorType, all = False):
        string = "FL 127.0.0.1 " + errorType

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
        
        if self.modo == 'debug':
            print(string)

    def TO(self, timeoutType, all = False):
        string = "TO " + timeoutType

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
        
        if self.modo == 'debug':
            print(string)

    def SP(self, reason, all = False):
        string = "SP 127.0.0.1 " + reason

        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
        
        if self.modo == 'debug':
            print(string)

    def ST(self, port, timeout, mode, all = False):
        string = "ST 127.0.0.1 " + port + " " + timeout + " " + mode
        
        if self.st:
            logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
            logging.info(string)
        else:
            if all:
                logging.basicConfig(filename = self.fileLogsAll, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
            else:
                logging.basicConfig(filename = self.fileLogs, filemode="a", level=logging.INFO, format= "%(asctime)s.%(msecs)03d %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')
                logging.info(string)
        
        if self.modo == 'debug':
            print(string)