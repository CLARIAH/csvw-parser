from rdflib import Graph, Namespace, BNode, RDF, Literal, URIRef, XSD
from rdflib.collection import Collection 
from uritemplate import expand
from dateutil.parser import parse
import json


def generate_object(url, row, metadata, collection):
    rowobject = {}
    rowobject['url'] = url + '#row=' + str(row.number + 1)
    rowobject['rownum'] = row.number
    
    
    
    
    cells = [] 
    cellsobject = {} 
    cells.append(cellsobject)
    
    for cell in row.cells:
        
        if cell.value != "": 
        


            
                index = int(str(cell.column)[-1:]) - 1 
                column_name = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#name'))
                if column_name is None: 
                    column_name = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#title'))
                
                cellsobject[column_name] = cell.value
                
#                 print collection[index]
                datatype = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#datatype'))
#                 print datatype 
                
                
                if isinstance(datatype, BNode):
                    base = metadata.value(datatype, URIRef('http://www.w3.org/ns/csvw#base'))
#                     print base 
                    format = metadata.value(datatype, URIRef('http://www.w3.org/ns/csvw#format'))
#                     print format 
                    
#                     if str(base) == "date": 
#                         print "date!!!"
                        
#                 
# dt = parse('Mon Feb 15 2010')
                
                
                


    rowobject['describes'] = cells
    return rowobject 
        





def minimal_mode(table, metadata):

#     if not metadata.get('suppressOutput', False):

#     for subj, pred, obj in metadata:
#         print subj, pred, obj 

    
    
    columncollections = list(metadata.subject_objects(URIRef('http://www.w3.org/ns/csvw#column')))
    for (s, collection_resource) in columncollections:
        collection = Collection(metadata, collection_resource)
    
    
    documentobject = {} 
    
    tables = []
    
    documentobject['tables'] = tables 
    
    
    tableobject = {}
    
    
    table.url = table.url.replace('w3c.github.io', 'www.w3.org/2013')
    tableobject['url'] = table.url
    
    try: 
        tableobject['dc:modified'] = list(metadata.subject_objects(URIRef('http://purl.org/dc/terms/modified')))[0][1] 
        tableobject['dc:license'] = list(metadata.subject_objects(URIRef('http://purl.org/dc/terms/license')))[0][1] 
        tableobject['dc:title'] = list(metadata.subject_objects(URIRef('http://purl.org/dc/terms/title')))[0][1] 
        
        
        keylist = list(metadata.subject_objects(URIRef('http://www.w3.org/ns/dcat#keyword')))
        keywords = []
        for (s, keyword) in keylist:
            keywords.append(str(keyword))
#             print keyword 
#         print keywords 
        tableobject['dcat:keyword'] = keywords
        
        
        publisherobject = {}
        PNode = list(metadata.subject_objects(URIRef('http://purl.org/dc/terms/publisher')))[0][1] 
        url = metadata.value(subject=PNode, predicate=URIRef('http://schema.org/url'))
        publisherobject['schema:url'] = url[:-1]  # json-ld parser adds trailing slash!? 
        name = metadata.value(subject=PNode, predicate=URIRef('http://schema.org/name'))
        publisherobject['schema:name'] = name 
        tableobject['dc:publisher'] = publisherobject
        

    except: 
        pass 
        
    tables.append(tableobject)
    

    
    rows = []
    for row in table.rows:
        rowjson = generate_object(table.url, row, metadata, collection)
        rows.append(rowjson)
    
    tableobject['row'] = rows
    documentjson = json.dumps(documentobject, indent=2)
    
    return documentjson
