import logging
# from dominio import Dominio

# Aspetos positivos : data está bem :)

#Como meter isto no ficheiro????
fstLine = "# Log File for DNS server/resolver"
test = "ola"
source = "SP"
logging.basicConfig(filename = "logs"+source+".log", filemode="a", level=logging.INFO, format= "%(asctime)s %(message)s", datefmt='%d:%m:%Y.%H:%M:%S')


def QR_QE():

    return 

def RP_RR():
    return

def ZT(port, role, time, totalbytes):
    return port + " " + role + " " + time + " " + totalbytes

def EV(msg):
    return msg

def ER():
    return  

def EZ(end, role):
    return end +" " +  role

def FL(errorType):
    return "127.0.0.1 " + errorType

def TO(timeoutType):
    return timeoutType

def SP(reason):
    return "127.0.0.1 " + reason

def ST(port,timeout,mode):
    return "127.0.0.1" + port + " " + timeout + " " + mode
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

logging.info(test)