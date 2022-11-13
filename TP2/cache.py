from datetime import datetime
import time

# Apesar do campo TimeStamp ser iniciado como uma string no futuro vai ser alterado para ser um objeto do tipo datetime
class Cache:

    def __init__(self):
        self.cache = []
        
        for i in range(64000):
            entrada = ['','','','','','','',str(i),'FREE']
            self.cache.append(entrada)

    def procuraEntradaValid(self, index, name, type):
        now = datetime.now()
        result = 64001

        while index <= 64000:
            if self.cache[index-1][5] == 'OTHERS':
                diff = now - self.cache[index-1][6]
                if diff.total_seconds() > float(self.cache[index-1][3]):
                    self.cache[index-1][8] = 'FREE'

            if self.cache[index-1][0] == name and self.cache[index-1][1] == type:
                result = index
            index += 1
        
        return result

    def procuraPrimeiraEntradaFree(self):

        for i in range(64000):
            if self.cache[i][8] == 'FREE':
                return i
        
        return 64001

    def procuraUltimaEntradaFree(self):
        i = 64000

        while i >= 0:
            if self.cache[i][8] == 'FREE':
                return i
            i -= 1
        
        return -1

    def procuraEntradaCompleta(self, name, type, value, order):

        for i in range(64000):
            if self.cache[i][0] == name and self.cache[i][1] == type and self.cache[i][2] == value and self.cache[i][4] == order:
                return i
        
        return 64001

    # Se calhar o ttl não é necessário receber
    # Esta função retorna false quando o pedido de registo de uma entrada é ignorado caso contrário retorna true
    def registaAtualizaEntrada(self, name, type, value, ttl, origin, order = ''):

        if origin == 'FILE' or origin == 'SP':
            index = self.procuraPrimeiraEntradaFree()
            self.cache[index][0] = name
            self.cache[index][1] = type
            self.cache[index][2] = value
            self.cache[index][3] = ttl
            self.cache[index][4] = order
            self.cache[index][5] = origin
            self.cache[index][6] = datetime.now()
            self.cache[index][8] = 'VALID'
        elif origin == 'OTHERS':
            index = self.procuraEntradaCompleta(name, type, value, order)
            if index <= 64000 and (self.cache[index][5] == 'SP' or self.cache[index][5] == 'FILE'):
                return False
            elif index <= 64000 and self.cache[index][5] == 'OTHERS':
                self.cache[index][0] = name
                self.cache[index][1] = type
                self.cache[index][2] = value
                self.cache[index][3] = ttl
                self.cache[index][4] = order
                self.cache[index][5] = origin
                self.cache[index][6] = datetime.now()
                self.cache[index][8] = 'VALID'
                return True
            elif index > 64000:
                index = self.procuraUltimaEntradaFree()
                self.cache[index][0] = name
                self.cache[index][1] = type
                self.cache[index][2] = value
                self.cache[index][3] = ttl
                self.cache[index][4] = order
                self.cache[index][5] = origin
                self.cache[index][6] = datetime.now()
                self.cache[index][8] = 'VALID'

    def limpaCache(self, name):

        for i in range(64000):
            if self.cache[i][0] == name:
                self.cache[i][8] = 'FREE'

