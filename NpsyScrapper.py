from PmcQuery import Search,Fetch
import json
import time
import datetime

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
    def formerFromNumerous(self,file):
        excededDict={}
        formerList=[]
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        for k,v in entries.items():            
            if len(v)>19:
                for x in entries[k]:                    
                    try:
                        dateObj=datetime.datetime(int(x['date']['year']),int(x['date']['month']),int(x['date']['day']))                        
                        if(k in excededDict):
                            excededDict[k]['dates'].append(dateObj)
                        else:                            
                            excededDict[k]={"id":x['id'],"dates":[dateObj]}                            
                    except Exception as e:
                        pass
        for k in excededDict:
            excededDict[k]["dates"].sort()
            d=excededDict[k]["dates"][0]
            formerList.append((k,excededDict[k]["id"],d,datetime.datetime(d.year-10, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, d.tzinfo)))         
        return formerList

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
    def expandQuery(self,file):
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            results=json.loads(content)
        queryList=self.formerFromNumerous(file)
        for x in queryList:            
            s=Search(x[0],"title",["PublicationDate",x[3].strftime("%Y/%m/%d"),x[2].strftime("%Y/%m/%d")])
            try:
                results[x[0]].append(s.getData(x[1],"all"))
            except Exception as e:
                print("Error while searching for ",x[0]," : ",e)                                                  
        with open(file,"w",encoding="utf-8") as f:
            content=json.dumps(results,indent=4)
            f.write(content)



