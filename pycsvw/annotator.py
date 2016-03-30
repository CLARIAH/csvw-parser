from rdflib import Graph, Namespace, BNode, RDF, Literal, URIRef, XSD
from rdflib.collection import Collection 

import datetime

def annotate_table(table, metadata): 
        
    # first start to generate annotated table          
    
    columncollections = list(metadata.subject_objects(URIRef('http://www.w3.org/ns/csvw#column')))
    for (s, collection_resource) in columncollections:
        collection = Collection(metadata, collection_resource)
    
    for column in table.columns:

        index = int(str(column)[-1:]) - 1 
                    
        column_name = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#name'))
        column.name = column_name             

        column_title = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#title'))
        column.titles.append(column_title)
        
        
        datatype = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#datatype'))
        column_datatype = datatype
        

        if isinstance(datatype, BNode):
            column_datatype = {} 
            base = metadata.value(datatype, URIRef('http://www.w3.org/ns/csvw#base'))
            column_datatype["base"] = base
            format = metadata.value(datatype, URIRef('http://www.w3.org/ns/csvw#format'))
            column_datatype["format"] = format
            
            # parse cells 
            for cell in column.cells: 
                if str(base) == "date": 
                    if str(format) == "M/d/yyyy": 
                        parsed_date = datetime.datetime.strptime(cell.value, '%m/%d/%Y').date()
                        cell.value = str(parsed_date)

        column.datatype = column_datatype
    
    return table, metadata 
        