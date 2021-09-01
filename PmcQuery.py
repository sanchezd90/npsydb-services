import requests
import re
import xmltodict
import json
from datetime import datetime

class Search():
    
    def __init__(self,term,splitTerm=False,field="title",filter=None,tool="my_tool",email="my_email@example.com",search_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term="):
        
        self.term=term.strip()
        self.filter=''        
        self.field=field.strip().lower()
        self.tool=tool.strip()
        self.email=email.strip()
        self.search_url=search_url.strip()

        if(splitTerm):
            self.term=self.term.replace(" ",f"%5B{field}%5DAND%20")

        if(filter!=None):
            if(filter[0]=="PublicationDate"):
                formerDate=filter[1].split("/")
                laterDate=filter[2].split("/")
                self.filter=f'AND%20"{formerDate[0]}%2F{formerDate[1]}%2F{formerDate[2]}"%5BPublication+Date%5D+%3A+"{laterDate[0]}%2F{laterDate[1]}%2F{laterDate[2]}"%5BPublication+Date%5D'              

    def url(self):
        print("Assembling url")
        print(f"""{self.search_url}{self.term.replace(" ","+")}%5B{self.field}%5D{self.filter}&tool={self.tool}&email={self.email}""")
        return f"""{self.search_url}{self.term.replace(" ","+")}%5B{self.field}%5D{self.filter}&tool={self.tool}&email={self.email}"""                            
    def response(self):
        print("Making request")
        return requests.get(self.url())        
    def stripIdElement(self,idElement):
        return idElement.strip("<Id>").strip("</Id>")    
    
    #--Retrieve IDs--#
    def getIds(self):
        idString=re.split("IdList",self.response().content.decode('UTF-8'))[1][1:-2]
        print("Gathering id list")
        print([self.stripIdElement(x) for x in idString.split("\n")][1:-1])
        return [self.stripIdElement(x) for x in idString.split("\n")][1:-1]
    
    #--Retrieve Document data--#
    def getData(self,key,*args):
        results=[]
        print("Retrieving documents")
        for id in self.getIds():
            f=Fetch(id)
            results.append(f.get(key,*args))                      
        print("All documents retrieved")
        return results
    def saveData(self,key,*args):
        results=[]
        print("Retrieving documents")
        for id in self.getIds():
            f=Fetch(id)
            results.append(f.get(key,*args))        
        with open(f"{self.term}.json","w",encoding="utf-8") as f:
            f.write(json.dumps(results,indent=4))  
        print("All documents retrieved")      

class Fetch():

    def __init__(self,id,tool="my_tool",email="my_email@example.com",fetch_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id="):

        self.id=id.strip()        
        self.tool=tool.strip()
        self.email=email.strip()
        self.fetch_url=fetch_url.strip()

    def url(self):   
        print("Assembling url")
        print(f"""{self.fetch_url}{self.id}&tool={self.tool}&email={self.email}"""    )     
        return f"""{self.fetch_url}{self.id}&tool={self.tool}&email={self.email}"""    

    def response(self):
        return requests.get(self.url())
    def toJson(self):
        return json.dumps(xmltodict.parse(self.response().content), indent=4)
    def save(self):
        with open(f"{self.id}.json","w",encoding="utf-8") as f:
            f.write(self.toJson())
    def toDict(self):
        return json.loads(self.toJson())
    def get(self,id,*args):
        print("Retrieving document data")
        stringData=str(self.response().content)
        data=self.toDict()["pmc-articleset"]["article"]        
        fieldDict= {
            "id":id,
            "retrieved":datetime.timestamp(datetime.now())
            }
        for arg in args:
            #--- ALL ---#
            if arg == "all":
                try:
                    fieldDict["journal-title"]=data["front"]["journal-meta"]["journal-title-group"]["journal-title"]                    
                    print(f"journal-title data retrieved (first method)")
                except Exception as e:
                    fieldDict["journal-title"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
                try:
                    for ids in data["front"]["article-meta"]["article-id"]:
                            if ids["@pub-id-type"]=="doi":
                                fieldDict["doi"]=ids["#text"]
                                print(f"doi data retrieved (first method)")
                except Exception as e:
                    fieldDict["doi"]="notFound"
                    print(f"Error in '{arg}' search ",e)                    
                 
                try:
                    for ids in data["front"]["article-meta"]["article-id"]:
                            if ids["@pub-id-type"]=="pmc":
                                fieldDict["pmc"]=ids["#text"]
                                print(f"pmc data retrieved (first method)")
                except Exception as e:
                    fieldDict["pmc"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
                try:
                    fieldDict["title"]=data["front"]["article-meta"]["title-group"]["article-title"]
                    print(f"title data retrieved (first method)")
                except Exception as e:
                    fieldDict["title"]="notFound"
                    print(f"Error in '{arg}' search ",e)
           
                try:                    
                    fieldDict["date"]=data["front"]["article-meta"]["pub-date"][0]
                    print(f"date data retrieved (first method)")
                except Exception as e:
                    fieldDict["date"]="notFound"
                    print(f"Error in date search (first method)",e)
                    try:
                        fieldDict["date"]=data["front"]["article-meta"]["pub-date"]
                        print(f"date data retrieved (second method)")
                    except Exception as e:                        
                        print(f"Error in date search (second method)",e)
                        try:
                            slice=re.split("pub-date",stringData)
                            fieldDict["date"]=slice[1]
                            print(f"date data retrieved (third method)")
                        except Exception as e:
                            fieldDict["date"]="notFound"
                            print(f"Error in date search (third method)",e)            
                try:
                    fieldDict["abstract"]=data["front"]["article-meta"]["abstract"]["p"]["#text"]
                    print(f"abstract data retrieved (first method)")
                except Exception as e:                    
                    print(f"Error in abstract search (first method)",e)
                    try:
                        fieldDict["abstract"]=data["front"]["article-meta"]["abstract"]["sec"]
                        print(f"abstract data retrieved (second method)")
                    except Exception as e:                        
                        print(f"Error in abstract search (second method)",e) 
                        try:
                            slice=re.split("abstract",stringData)[1][3:-3]
                            components=re.split("<sec>",slice)
                            fieldDict["abstract"]=components
                            print(f"abstract data retrieved (third method)")
                        except Exception as e:                        
                            print(f"Error in abstract search (third method)",e) 
                            fieldDict["abstract"]="notFound"

                try:
                    fieldDict["keywords"]=data["front"]["article-meta"]["kwd-group"]["kwd"]
                    print(f"keywords data retrieved (first method)")
                except Exception as e:
                    print(f"Error in keywords search (first method)",e)
                    try:
                        fieldDict["keywords"]=data["front"]["article-meta"]["kwd-group"][0]["kwd"]
                        print(f"keywords data retrieved (second method)")
                    except Exception as e:
                        print(f"Error in keywords search (second method)",e)
                        try:
                            slice=re.split("kwd-group",stringData)
                            fieldDict["keywords"]=slice[1]
                            print(f"keywords data retrieved (third method)")
                        except Exception as e:
                            fieldDict["keywords"]="notFound"
                            print(f"Error in keywords search (third method)",e)

                return fieldDict 
            #--- JOURNAL TITLE ---#
            elif arg == "journal-title":
                try:
                    fieldDict["journal-title"]=data["front"]["journal-meta"]["journal-title-group"]["journal-title"]
                    print(f"journal-title data retrieved")
                except Exception as e:
                    fieldDict["journal-title"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
            #--- DOI ---#
            elif arg == "doi":
                try:
                    for ids in data["front"]["article-meta"]["article-id"]:
                            if ids["@pub-id-type"]=="doi":
                                fieldDict["doi"]=ids["#text"]
                                print(f"doi data retrieved")
                except Exception as e:
                    fieldDict["doi"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
            #--- PMC ---#
            elif arg == "doi":
                try:
                    for ids in data["front"]["article-meta"]["article-id"]:
                            if ids["@pub-id-type"]=="pmc":
                                fieldDict["pmc"]=ids["#text"]
                                print(f"pmc data retrieved")
                except Exception as e:
                    fieldDict["pmc"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
            #--- TITLE ---#
            elif arg == "title":
                try:
                    fieldDict["title"]=data["front"]["article-meta"]["title-group"]["article-title"]
                    print(f"title data retrieved")
                except Exception as e:
                    fieldDict["title"]="notFound"
                    print(f"Error in '{arg}' search ",e)
           
            #--- DATE ---#
            elif arg == "date":
                try:                    
                    fieldDict["date"]=data["front"]["article-meta"]["pub-date"][0]
                    print(f"date data retrieved")
                except Exception as e:
                    fieldDict["date"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
            #--- ABSTRACT ---#
            elif arg == "abstract":
                try:
                    fieldDict["abstract"]=data["front"]["article-meta"]["abstract"]["p"]["#text"]
                    print(f"abstract data retrieved")
                except Exception as e:
                    fieldDict["abstract"]="notFound"
                    print(f"Error in '{arg}' search ",e)
            
            #--- KEYWORDS ---#
            elif arg == "keywords":
                try:
                    fieldDict["keywords"]=data["front"]["article-meta"]["kwd-group"]["kwd"]
                    print(f"keywords data retrieved")
                except Exception as e:
                    fieldDict["keywords"]="notFound"
                    print(f"Error in '{arg}' search ",e)
        
        return fieldDict
    