from rdflib import Graph, Namespace, BNode, RDF, Literal, URIRef, XSD
from rdflib.collection import Collection 

import re
import datetime

# first steps towards annotated table   

def annotate_table(table, metadata): 

    columncollections = list(metadata.subject_objects(URIRef('http://www.w3.org/ns/csvw#column')))
    for (s, collection_resource) in columncollections:
        collection = Collection(metadata, collection_resource)
        
    primaryKey = metadata.value(s, URIRef('http://www.w3.org/ns/csvw#primaryKey'))
    aboutURL = metadata.value(s, URIRef('http://www.w3.org/ns/csvw#aboutUrl'))

    if aboutURL != None: 
        aboutColumn = re.search('%s(.*)%s' % ('{', '}'), aboutURL).group(1)

    
    for column in table.columns:

        index = int(str(column)[-1:]) - 1 

        column_name = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#name'))
        column.name = column_name

        if (column.name != None) and (column.name == primaryKey):
            for row in table.rows: 
                row.primary_key = row.cells[index]

        
        if (column.name != None) and (str(column.name) == str(aboutColumn)):
            for row in table.rows: 
                for cell in row.cells: 
                    cell.about_url = aboutURL.replace('{' + aboutColumn + '}', row.cells[index].value)

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
        