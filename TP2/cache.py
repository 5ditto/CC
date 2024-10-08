from datetime import datetime

# Apesar do campo TimeStamp ser iniciado como uma string no futuro vai ser alterado para ser um objeto do tipo datetime
class Cache:

    def __init__(self):
        self.cache = []
        self.nrEntradas = 300
        
        for i in range(300):
            entrada = ['','','','','','','',str(i),'FREE']
            self.cache.append(entrada)

    def procuraEntradaValid(self, index, name, type):
        now = datetime.now()
        result = -1
        
        while index <= 300:
            if self.cache[index-1][5] == 'OTHERS':
                diff = now - self.cache[index-1][6]
                if diff.total_seconds() > float(self.cache[index-1][3]):
                    self.cache[index-1][8] = 'FREE'

            if self.cache[index-1][0] == name and self.cache[index-1][1] == type:
                result = index
            index += 1
        
        return result

    def todasEntradasValid(self, index, name, type):
        result = []

        while index <= 300:
            if self.cache[index-1][0] == name and self.cache[index-1][1] == type:
                result.append(index)
            index += 1

        return result

    def campoValor(self, index):
        if index <= self.nrEntradas:
            return self.cache[index-1][2]
        return ''

    def entrada(self, index):
        entrada = ''
        if index <= self.nrEntradas and index > 0:
            if self.cache[index-1][4] == '':
                entrada = self.cache[index-1][0] + " " + self.cache[index-1][1] + " " + self.cache[index-1][2] + " " + self.cache[index-1][3]
            else:
                entrada = self.cache[index-1][0] + " " + self.cache[index-1][1] + " " + self.cache[index-1][2] + " " + self.cache[index-1][3] + " " + self.cache[index-1][4]

        return entrada

    def procuraPrimeiraEntradaFree(self):

        for i in range(300):
            if self.cache[i][8] == 'FREE':
                return i
        
        return -1

    def procuraUltimaEntradaFree(self):
        i = 299

        while i >= 0:
            if self.cache[i][8] == 'FREE':
                return i
            i -= 1
        
        return -1

    def procuraEntradaCompleta(self, name, typeValue, value, order):

        for i in range(300):
            if self.cache[i][0] == name and self.cache[i][1] == typeValue and self.cache[i][2] == value and self.cache[i][4] == order:
                return i
        
        return -1

    # Se calhar o ttl não é necessário receber
    # Esta função retorna false quando o pedido de registo de uma entrada é ignorado caso contrário retorna true
    def registaAtualizaEntrada(self, name, typeValue, value, ttl, origin, order = ''):

        if origin == 'FILE' or origin == 'SP':
            index = self.procuraPrimeiraEntradaFree()
            self.cache[index][0] = name
            self.cache[index][1] = typeValue
            self.cache[index][2] = value
            self.cache[index][3] = ttl
            self.cache[index][4] = order
            self.cache[index][5] = origin
            self.cache[index][6] = datetime.now()
            self.cache[index][8] = 'VALID'
            return index
        elif origin == 'OTHERS':
            index = self.procuraEntradaCompleta(name, typeValue, value, order)
            if index >= 0 and index <= 300 and (self.cache[index][5] == 'SP' or self.cache[index][5] == 'FILE'):
                return -1
            elif index >= 0 and index <= 300 and self.cache[index][5] == 'OTHERS':
                self.cache[index][0] = name
                self.cache[index][1] = typeValue
                self.cache[index][2] = value
                self.cache[index][3] = ttl
                self.cache[index][4] = order
                self.cache[index][5] = origin
                self.cache[index][6] = datetime.now()
                self.cache[index][8] = 'VALID'
                return index
            elif index == -1:
                index = self.procuraUltimaEntradaFree()
                self.cache[index][0] = name
                self.cache[index][1] = typeValue
                self.cache[index][2] = value
                self.cache[index][3] = ttl
                self.cache[index][4] = order
                self.cache[index][5] = origin
                self.cache[index][6] = datetime.now()
                self.cache[index][8] = 'VALID'
                return index
    
    def limpaCache(self, name):

        for i in range(300):
            if self.cache[i][0] == name:
                self.cache[i][8] = 'FREE'
    
    # Esta função serve para debug da cache
    def printaEntradasValid(self):  
        
        for i in range(300):
            if self.cache[i][8] == 'VALID':
                print(self.cache[i])