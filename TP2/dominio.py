import re

class Dominio:

    def __init__(self, ficheiroConfig):
        self.name = ''
        self.ficheiroConfig = ficheiroConfig
        self.ficheiroDb = ''
        self.ficheiroSTs = ''
        self.ficheiroLogsAll = ''
        self.ficheiroLogs = ''
        self.endSP = ''
        self.endSS = [] # Lista de strings dos ip's dos SS 
        self.endSR = ''
        self.endSTs = []

    def parseFicheiroConfig(self):
        f = open(self.ficheiroConfig, "r")

        for line in f:
            lista = re.split(" ", line)
            if lista[0] != "#":
                if lista[0] == 'all':
                    self.ficheiroLogsAll = lista[2].replace('\n', '')
                elif lista[0] == 'root':
                    self.ficheiroSTs = lista[2]
                else:
                    self.name = lista[0]
                    if lista[1] == 'DB':
                        self.ficheiroDb = lista[2].replace('\n', '')
                    
                    if lista[1] == 'SP':
                        self.endSP = lista[2]
                    
                    if lista[1] == 'SS':
                        self.endSS.append(lista[2].replace('\n', ''))
                    
                    if lista[1] == 'DD':
                        self.endSR = lista[2]
                    
                    if lista[1] == 'LG':
                        self.ficheiroLogs = lista[2].replace('\n', '')

        f.close() 

    def parseFicheiroListaST(self):
        f = open(self.ficheiroSTs, "r")

        for line in f:
            if line[0] != "#":
                splited = re.split(":", line)
                splited[1] = splited[1].replace('\n','')
                self.endSTs.append((splited[0],splited[1]))

        f.close() 

    def __str__(self):
        string = "Nome: " + self.name + "\nDB: " + self.ficheiroDb + "\nEndereço SP: " + self.endSP + "\nEndereços SS: "

        for end in self.endSS:
            string += end + ", "

        string = string[:-2]
        string += "\nDD: " + self.endSR

        string += "\nFicheiro dos ST's: " + self.ficheiroSTs + "\nFicheiro Logs: " + self.ficheiroLogs + "\n"
        string += "Endereços e portas dos ST's: \n"
        for add in self.endSTs:
            string += str(add)

        return string

#dom = Dominio("config.txt")
#dom.parseFicheiroConfig()
#dom.parseFicheiroListaST()
#print(dom)



#def parseFicheiroBaseDados(self, ficheiro = None):
#
#        if ficheiro == None:
#            self.ficheiroDb = self.ficheiroDb[:-1]
#            ficheiro = self.ficheiroDb
#
#        f = open(ficheiro, "r")
#        # Servidores Autoritários
#        self.db["A"] = dict()
#        nrEntradas = 0
#
#        for line in f:
#            nrEntradas += 1
#            lista = re.split(" ", line)
#
#            if lista[0] != "#":
#                if lista[0] == "TTL":
#                    self.db['TTL'] = lista[2][:-1]
#                elif lista[1] == "A":
#                    valor = ''
#                    i = 2
#                    while i < len(lista):
#                        valor += lista[i] + " "
#                        i += 1
#                    valor = valor[:-2]
#                    self.db["A"][lista[0]] = valor
#                elif lista[1] == "SOASERIAL":
#                    self.db['SOASERIAL'] = lista[2]
#                else:
#                    # Se a chave ainda não existir no dicionario associamo-la a um set de valores
#                    if lista[1] not in self.db.keys():
#                        self.db[lista[1]] = set()
#
#                    if len(lista) < 4: # Se o lista[2] for o ultimo elemento retiramos o '\n'
#                        self.db[lista[1]].add(lista[2][:-1])
#                    else:
#                        valor = ''
#                        i = 2
#                        while i < len(lista):
#                            valor += lista[i] + " "
#                            i += 1 
#                        valor = valor[:-2]
#                        self.db[lista[1]].add(valor)   
#
#        self.db['nrEntradas'] = nrEntradas
#        f.close()
#
#    # Esta função serve para fazer o parse da string que o SS ficou depois de fazer a transferência de zona com o SP
#    # Transforma essa string na nova base de dados do SS
#    # Se calhar é boa ideia mudar esta função para o SS
#    def parseStringParaDB(self, baseDeDados):
#        # baseDeDados -> String
#        # Servidores Autoritários
#        self.db["A"] = dict()
#        lista = re.split("\n", baseDeDados)
#        i = 0
#        for item in lista:
#            lista[i] = re.split(" ", item)
#            i += 1
#
#        for linha in lista:
#
#            if linha[1] != "#":
#                if linha[1] == "TTL":
#                    self.db['TTL'] = linha[3][:-1]
#                elif linha[2] == "A":
#                    valor = ''
#                    i = 3
#                    while i < len(linha):
#                        valor += linha[i] + " "
#                        i += 1
#                    valor = valor[:-2]
#                    self.db["A"][linha[1]] = valor
#                elif linha[2] == "SOASERIAL":
#                    self.db['SOASERIAL'] = linha[3]
#                else:
#                    # Se a chave ainda não existir no dicionario associamo-la a um set de valores
#                    if linha[2] not in self.db.keys():
#                        self.db[linha[2]] = set()
#
#                    if len(linha) < 4: # Se o lista[2] for o ultimo elemento retiramos o '\n'
#                        self.db[linha[2]].add(linha[3][:-1])
#                    else:
#                        valor = ''
#                        i = 3
#                        while i < len(linha):
#                            valor += linha[i] + " "
#                            i += 1 
#                        valor = valor[:-2]
#                        self.db[linha[2]].add(valor)