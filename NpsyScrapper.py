from PmcQuery import Search,Fetch
import json
import time

class NpsyScrapper():
          
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
    def basicQuery(self,source,destination,idRange,sleep,*args):
        if type(idRange)!=list:
            idRange=[idRange,idRange+1]
        print(type(idRange))
        with open(source,"r",encoding="utf-8") as f:
            content=f.read()
            pruebas=json.loads(content)
        with open(destination,"r",encoding="utf-8") as f:
            content=f.read()
            results=json.loads(content)
        for id in range(int(idRange[0]),int(idRange[1])):
            print(id)
            for prueba in pruebas:
                print(prueba)
                if prueba['id']==str(id):
                    for arg in args:
                        s=Search(f"{prueba['nombre_principal']} {arg}","title","npsydb","sanchezd90@gmail.com")                    
                        if f"{prueba['nombre_principal']} {arg}" in results:                                                        
                            results[f"{prueba['nombre_principal']} {arg}"].append(s.getData(id,"all"))
                        else:
                            results[f"{prueba['nombre_principal']} {arg}"]=s.getData(id,"all")
                    for arg in args:
                        s=Search(f"{prueba['acronym']} {arg}","title","npsydb","sanchezd90@gmail.com")                    
                        if f"{prueba['acronym']} {arg}" in results:
                            results[f"{prueba['acronym']} {arg}"].append(s.getData(id,"all"))
                        else:
                            results[f"{prueba['acronym']} {arg}"]=s.getData(id,"all")
                    s=Search(f"{prueba['nombre_principal']}","title","npsydb","sanchezd90@gmail.com")                
                    if f"{prueba['nombre_principal']}" in results:
                        results[f"{prueba['nombre_principal']}"].append(s.getData(id,"all"))
                    else:
                        results[f"{prueba['nombre_principal']}"]=s.getData(id,"all")
                    s=Search(f"{prueba['acronym']}","title","npsydb","sanchezd90@gmail.com")                
                    if f"{prueba['acronym']}" in results:
                        results[f"{prueba['nombre_principal']}"].append(s.getData(id,"all"))
                    else:
                        results[f"{prueba['nombre_principal']}"]=s.getData(id,"all")
            print("Time to sleep")
            time.sleep(sleep)
        with open(destination,"w",encoding="utf-8") as f:
            content=json.dumps(results,indent=4)
            f.write(content)

n=NpsyScrapper()
n.basicQuery("pruebas.json","results.json",["239","240"],60,"norms","normative data")
