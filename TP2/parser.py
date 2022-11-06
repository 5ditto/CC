class Dominio:

    def __init__(self):
        self.name = ''
        self.db = ''
        self.endSP = ''
        self.endSS = [] # Lista de strings dos ip's dos SS 
        self.endSR = ''
        self.ficheiroSTs = ''
        self.ficheiroLogs = ''

    def parserFicheiroDBSP(self, file):
        f = open(file, "r")
        
        nrword = 1
        tipo = ''

        for line in f:
            for word in line.split():

                if nrword == 1:
                    if word != "all" and word != "root":
                        self.name = word 
                    
                    if word == "#":
                        break
                
                if nrword == 2:
                    tipo = word

                if nrword == 3:

                    if tipo == "DB":
                        self.db = word

                    if tipo == "SP":
                        self.endSP = word

                    if tipo == "SS":
                        self.endSS.append(word)

                    if tipo == "DD":
                        self.endSR = word

                    if tipo == "ST":
                        self.ficheiroSTs = word

                    if tipo == "LG":
                        self.ficheiroLogs = word
                    
                nrword += 1

            nrword = 1
        
        f.close() 

    def parserFicheiroConfig(self, file):
        f = open(file, "r")


        f.close() 

    def parserFicheiroLog(self, file):
        f = open(file, "r")

        f.close() 

    def parserFicheiroListaST(self,file):
        f = open(file, "r")

        f.close() 

    def __str__(self):
        string = "Nome: " + self.name + "\nDB: " + self.db + "\nEndereço SP: " + self.endSP + "\nEndereços SS: "

        for end in self.endSS:
            string += end + ", "

        string = string[:-2]
        string += "\nDD: " + self.endSR

        string += "\nFicheiro dos ST's: " + self.ficheiroSTs + "\nFicheiro Logs: " + self.ficheiroLogs + "\n"
        return string


d = Dominio()
d.parserFicheiroDBSP("ex.txt")
print(d)

