from rdflib import Graph, Namespace, BNode, RDF, Literal, URIRef, XSD
from rdflib.collection import Collection 
from uritemplate import expand
from dateutil.parser import parse
import json


def generate_object(url, row, metadata):
    rowobject = {}
    rowobject['url'] = url + '#row=' + str(row.number + 1)
    rowobject['rownum'] = row.number

        
    cells = [] 
    cellsobject = {} 
    cells.append(cellsobject)
    
    
    # quite a hack, will have to be generalized 
    cellsobject['@id'] = row.cells[0].about_url
    
    for cell in row.cells:
        
        if cell.value != "": 
            
            column_name = cell.column.name 
            if column_name is None: 
                column_name = cell.column.titles[0] 

            cellsobject[column_name] = cell.value


    rowobject['describes'] = cells
    return rowobject 
        



def minimal_mode(table, metadata):
    
    documentobject = {} 
    
    tables = []
    
    documentobject['tables'] = tables 
    
    
    tableobject = {}
    
    
    # ugly hack for test cases 
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
        rowjson = generate_object(table.url, row, metadata)
        rows.append(rowjson)
    
    tableobject['row'] = rows
    documentjson = json.dumps(documentobject, indent=2)
    
    return documentjson
