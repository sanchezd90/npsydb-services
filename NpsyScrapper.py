from PmcQuery import Search,Fetch
import json
import time

class NpsyScrapper():
    def __init__(self):
        self.results={}
    #--File management--#
    def mergeDict(self,main,secondary,primaryKey,foreignKey):
        #merge dictionaries for pruebas and denominaciones
        with open(f"{secondary}.json","r",encoding="utf-8") as f:
            content=f.read()
            secondaryContent=json.loads(content)

        with open(f"{main}.json","r",encoding="utf-8") as f:
            content=f.read()
            mainContent=json.loads(content)

        for s in secondaryContent:
            for m in mainContent:
                if s[foreignKey]==m[primaryKey]:
                    del s[foreignKey]
                    for k,v in s.items():
                        m[k]=v

        with open(f"{main}.json","w",encoding="utf-8") as f:
            content=json.dumps(mainContent,indent=4)
            f.write(content)
    
    #--Query management--#
    def basicQuery(self,source,idRange,sleep,*args):
        if type(idRange)!=list:
            idRange=[idRange,idRange+1]
        with open(source,"r",encoding="utf-8") as f:
            content=f.read()
            pruebas=json.loads(content)
        for prueba in pruebas:
            for id in range(int(idRange[0]),int(idRange[1])):
                if prueba['id']==id:
                    for arg in args:
                        s=Search(f"{prueba['nombre_principal']} {arg}","title","npsydb","sanchezd90@gmail.com")                    
                        self.results[f"{prueba['nombre_principal']} {arg}"]=s.getData(id,"all")
                    for arg in args:
                        s=Search(f"{prueba['acronym']} {arg}","title","npsydb","sanchezd90@gmail.com")                    
                        self.results[f"{prueba['acronym']} {arg}"]=s.getData(id,"all")
                    s=Search(f"{prueba['nombre_principal']}","title","npsydb","sanchezd90@gmail.com")                
                    self.results[f"{prueba['nombre_principal']}"]=s.getData(id,"all")
                    s=Search(f"{prueba['acronym']}","title","npsydb","sanchezd90@gmail.com")                
                    self.results[f"{prueba['acronym']}"]=s.getData(id,"all")
            with open(f"{id}.json","w",encoding="utf-8") as f:
                content=json.dumps(self.results,indent=4)
                f.write(content)
            time.sleep(sleep)



