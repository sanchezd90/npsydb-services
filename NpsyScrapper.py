from PmcQuery import Search,Fetch
import json
import time
import datetime

class NpsyScrapper():
          
    #--File management--#
    def mergeDict(self,main,secondary,primaryKey,foreignKey):
        #merge dictionaries that share a common key
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
    
    def mergeFiles(self,mainFile,secondaryFile,targetFile):
        newFile={}
        with open(mainFile,"r",encoding="utf-8") as f:
            content=f.read()
            main=json.loads(content)
        with open(secondaryFile,"r",encoding="utf-8") as f:
            content=f.read()
            secondary=json.loads(content)
        for key in main:
            for result in main[key]:                
                if result["id"] not in newFile:
                    newFile[result["id"]]={result["pmc"]:result}
                else:
                    newFile[result["id"]].update({result["pmc"]:result})
        for key in secondary:
            for result in secondary[key]:
                try:
                    if result["id"] not in newFile:
                        newFile[result["id"]]={result["pmc"]:result}
                    else:
                        newFile[result["id"]].update({result["pmc"]:result})
                except:
                    print("Error in ",result)
        with open(targetFile,"w",encoding="utf-8") as f:
            content=json.dumps(newFile,indent=4)
            f.write(content)

    #--Stats--#
    def count(self,file):
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        for k,v in entries.items():
            print(f"{k}: {len(v)}")
    def length(self,file):
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        print(f"{len(entries)} terms")
        for term in entries:
            print(f"{term}: {len(entries[term])}")
    def getMax(self,file):
        frequencies=[]
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        for k,v in entries.items():
            frequencies.append(len(v))            
        return max(frequencies)
    def formerFromNumerous(self,file):
        excededDict={}
        formerList=[]
        with open(file,"r",encoding="utf-8") as f:
            content=f.read()
            entries=json.loads(content)
        for k,v in entries.items():            
            if len(v)>self.getMax(file)-1:
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
    def testQuery(self,source,termKey,splitTerm,field,filter,destination,idRange,sleep,includeRoot,*args):
        if type(idRange)!=list:
            idRange=[idRange,idRange+1]        
        with open(source,"r",encoding="utf-8") as f:
            content=f.read()
            terms=json.loads(content)
        with open(destination,"r",encoding="utf-8") as f:
            content=f.read()
            results=json.loads(content)
        for id in range(int(idRange[0]),int(idRange[1])):            
            for term in terms:                
                if term['id']==str(id):
                    print(id)
                    print(term)
                    for arg in args:
                        s=Search(f"{term[termKey]} {arg}",splitTerm,field,filter,"npsydb","sanchezd90@gmail.com")                    
                        if f"{term[termKey]} {arg}" in results:                                                        
                            results[f"{term[termKey]} {arg}"].append(s.getData(id,"all"))
                        else:
                            results[f"{term[termKey]} {arg}"]=s.getData(id,"all")                    
                    s=Search(f"{term[termKey]}",splitTerm,field,filter,"npsydb","sanchezd90@gmail.com")                
                    if includeRoot:
                        if f"{term[termKey]}" in results:
                            results[f"{term[termKey]}"].append(s.getData(id,"all"))
                        else:
                            results[f"{term[termKey]}"]=s.getData(id,"all")                        
            print("Time to sleep")
            time.sleep(sleep)
            print("Back to work")
        with open(destination,"w",encoding="utf-8") as f:
            content=json.dumps(results,indent=4)
            f.write(content)
    def refQuery(self,source,termKey,idKey,field,filter,destination,sleep):      
        with open(source,"r",encoding="utf-8") as f:
            content=f.read()
            terms=json.loads(content)
        with open(destination,"r",encoding="utf-8") as f:
            content=f.read()
            results=json.loads(content)                
            for term in terms:
                s=Search(f"{term[termKey]}",True,field,filter,"npsydb","sanchezd90@gmail.com")                                                                  
                if f"{term[termKey]}" in results:
                    results[term[idKey]].append(s.getData(term[idKey],"all"))
                else:
                    results[term[idKey]]=[s.getData(term[idKey],"all")]                       
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
            s=Search(x[0],True,"title",["PublicationDate",x[3].strftime("%Y/%m/%d"),x[2].strftime("%Y/%m/%d")])
            try:                
                document=s.getData(x[1],"all")
                for element in document:
                    results[x[0]].append(element)
            except Exception as e:
                print("Error while searching for ",x[0]," : ",e)                                                  
        with open(file,"w",encoding="utf-8") as f:
            content=json.dumps(results,indent=4)
            f.write(content)



