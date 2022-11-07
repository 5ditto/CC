import re

class Dominio:

    def __init__(self):
        self.name = ''
        self.ficheiroDb = ''
        self.endSP = ''
        self.endSS = [] # Lista de strings dos ip's dos SS 
        self.endSR = ''
        self.ficheiroSTs = ''
        self.ficheiroLogs = ''
        self.endSTs = []
        self.db = dict()

    def parseFicheiroConfig(self, file):
        f = open(file, "r")

        for line in f:
            lista = re.split(" ", line)
            if lista[0] != "#":
                if lista[0] == 'all':
                    self.ficheiroLogs = lista[2]
                elif lista[0] == 'root':
                    self.ficheiroSTs = lista[2]
                else:
                    self.name = lista[0]
                    if lista[1] == 'DB':
                        self.ficheiroDb = lista[2]
                    
                    if lista[1] == 'SP':
                        self.endSP = lista[2]
                    
                    if lista[1] == 'SS':
                        self.endSS.append(lista[2])
                    
                    if lista[1] == 'DD':
                        self.endSR = lista[2]
                    
                    if lista[1] == 'LG':
                        self.ficheiroLogs = lista[2]

        f.close() 

    def parseFicheiroListaST(self):
        f = open(self.ficheiroSTs, "r")

        for line in f:
            if line[0] != "#":
                splited = re.split("\:|\]", line)
                splited[0] = splited[0][:-1]
                self.endSTs.append((splited[0],splited[1]))

        f.close() 

    def parseFicheiroBaseDadosSP(self):
        self.ficheiroDb = self.ficheiroDb[:-1]
        f = open(self.ficheiroDb, "r")

        for line in f:
            lista = re.split(" ", line)

            if lista[0] != "#":
                if len(lista) < 4: # Se o lista[2] for o ultimo elemento retiramos o '\n'
                    self.db[lista[1]] = lista[2][:-1]
                else:
                    self.db[lista[1]] = lista[2]

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
        
        string += "\n" + str(self.db)
        return string


d = Dominio()
d.parseFicheiroConfig("config.txt")
d.parseFicheiroListaST()
d.parseFicheiroBaseDadosSP()
print(d)