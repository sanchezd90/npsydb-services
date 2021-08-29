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
    
    def cleanFile(self,file):
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        newDict={}
        for k,v in entries.items():
            if len(v)>0:
                newDict.update({k:v})
        print(len(newDict))
        with open(file,"w",encoding="utf-8") as f:
            doc=json.dumps(newDict,indent=4)
            f.write(doc)

    #--Stats--#
    def count(self,file):
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        for k,v in entries.items():
            print(f"{k}: {len(v)}")
            if len(v)==20:
                for x in entries[k]:
                    print(x['date'])


    #--Query management--#
    def basicQuery(self,source,destination,idRange,sleep,includeRoot,*args):
        if type(idRange)!=list:
            idRange=[idRange,idRange+1]        
        with open(source,"r",encoding="utf-8") as f:
            content=f.read()
            pruebas=json.loads(content)
        with open(destination,"r",encoding="utf-8") as f:
            content=f.read()
            results=json.loads(content)
        for id in range(int(idRange[0]),int(idRange[1])):            
            for prueba in pruebas:                
                if prueba['id']==str(id):
                    print(id)
                    print(prueba)
                    for arg in args:
                        s=Search(f"{prueba['nombre_principal']} {arg}","title","npsydb","sanchezd90@gmail.com")                    
                        if f"{prueba['nombre_principal']} {arg}" in results:                                                        
                            results[f"{prueba['nombre_principal']} {arg}"].append(s.getData(id,"all"))
                        else:
                            results[f"{prueba['nombre_principal']} {arg}"]=s.getData(id,"all")                    
                    s=Search(f"{prueba['nombre_principal']}","title","npsydb","sanchezd90@gmail.com")                
                    if includeRoot:
                        if f"{prueba['nombre_principal']}" in results:
                            results[f"{prueba['nombre_principal']}"].append(s.getData(id,"all"))
                        else:
                            results[f"{prueba['nombre_principal']}"]=s.getData(id,"all")                        
            print("Time to sleep")
            time.sleep(sleep)
            print("Back to work")
        with open(destination,"w",encoding="utf-8") as f:
            content=json.dumps(results,indent=4)
            f.write(content)

n=NpsyScrapper()
#n.basicQuery("pruebas.json","new.json",["239","347"],1,True,"norms","normative data","validity")
n.count("results.json")

