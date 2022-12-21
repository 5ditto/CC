import re

class Dominio:

    def __init__(self, ficheiroConfig):
        self.name = ''
        self.endIp = ''
        self.endPorta = ''
        self.ficheiroConfig = ficheiroConfig
        self.ficheiroDb = ''
        self.ficheiroSTs = ''
        self.ficheiroLogsAll = ''
        self.ficheiroLogs = ''
        self.endSP = ''
        self.endSS = [] # Lista de strings dos ip's dos SS 
        self.endDD = [] # Lista de endereços que têm permissão para fazer queries sobre este domínio (no caso de ser SS ou SP)
        # No caso de ser um SR representa a lista de servidores que se podem contactar diretamente para fazer querys
        # No caso de ser um SR, a lista representa o endereço para o qual o SR deve encaminhar as queries sempre que não tenha a resposta na sua cache
        self.endSTs = []

    def parseFicheiroConfig(self):
        f = open(self.ficheiroConfig, "r")

        for line in f:
            lista = re.split(" ", line)
            if lista[0] != "#":
                if lista[0] == 'all':
                    self.ficheiroLogsAll = lista[2].replace('\n', '')
                elif lista[0] == 'root':
                    self.ficheiroSTs = lista[2].replace('\n', '')
                else:
                    self.name = lista[0]
                    if lista[1] == 'DB':
                        self.ficheiroDb = lista[2].replace('\n', '')
                    
                    if lista[1] == 'SP':
                        self.endSP = lista[2].replace('\n', '')
                    
                    if lista[1] == 'SS':
                        self.endSS.append(lista[2].replace('\n', ''))
                    
                    if lista[1] == 'DD':
                        self.endDD.append(lista[2].replace('\n', ''))
                    
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

    def encontraNomeTTLDom(self):
        file = open(self.ficheiroDb, "r")
        name = ''
        ttl = ''

        for line in file:
            x = re.split(" ", line)
            if x[0] != "#" and x[0] != '\n': # Se o x[0] é um '\n' então estamos numa linha vazia
                if x[1] == 'DEFAULT' and x[0] == '@': 
                    name = x[2]

                if x[1] == 'DEFAULT' and x[0] == 'TTL':
                    ttl = x[2][:-1]

                if name != '' and ttl != '':
                    return name, ttl 
        
        file.close()
        return name, ttl

    def parseDB(self, cache, logs, server):
        name, ttl = self.encontraNomeTTLDom()
        name = name[:-1]
        f = open(self.ficheiroDb, "r")

        for line in f:
            line = line.replace("\n", "")
            splited = re.split(' ', line)
            if splited[0] != "#" and len(splited) > 1:
                if len(splited) >= 5 and splited[0] == '@':
                    cache.registaAtualizaEntrada(name, splited[1], splited[2], ttl, 'FILE', splited[4])
                elif len(splited) >= 5 and splited[0] != '@':
                    cache.registaAtualizaEntrada(splited[0], splited[1], splited[2], ttl, 'FILE', splited[4])
                elif len(splited) < 5 and splited[0] == '@':
                    cache.registaAtualizaEntrada(name, splited[1], splited[2], ttl, 'FILE')
                else:
                    cache.registaAtualizaEntrada(splited[0], splited[1], splited[2], ttl, 'FILE')
            
            logs.EV("Registada entrada na cache do " + server)
        
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

