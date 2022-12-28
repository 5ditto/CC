import sys
from dominio import Dominio
from logs import Logs
from cache import Cache
from query import Query

class SR:

    def __init__(self):
        self.portaAtendimento = sys.argv[2]
        self.dom = Dominio(sys.argv[1]) # O primeiro parâmetro do programa é o seu ficheiro config
        self.dom.parseFicheiroConfig()
        self.dom.parseFicheiroListaST()
        self.logs = Logs(self.dom.ficheiroLogs, self.dom.ficheiroLogsAll, sys.argv[4])
        self.logs.ST(self.portaAtendimento, sys.argv[3], sys.argv[4])
        self.logs.EV('ficheiro de configuração lido')
        self.logs.EV('ficheiro de STs lido')
        self.logs.EV('criado ficheiro de logs')
        self.cache = Cache()
        self.logs.EV('cache iniciada')
        self.query = Query(True, self.dom, self.cache, self.logs, self.portaAtendimento)
        
sr = SR()
sr.query.recebeQuerysDoCL()