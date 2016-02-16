from rdflib import Graph, Namespace, BNode, RDF, Literal, URIRef, XSD
from rdflib.collection import Collection 

import iribaker
import sys, traceback

CSVW = Namespace('http://www.w3.org/ns/csvw#')
MAJOR = Namespace('http://data.socialhistory.org/vocab/hisco/majorGroup/')
MINOR = Namespace('http://data.socialhistory.org/vocab/hisco/minorGroup/')
UNIT  = Namespace('http://data.socialhistory.org/vocab/hisco/unitGroup/')
CATEGORY = Namespace('http://data.socialhistory.org/vocab/hisco/category/')
SKOS  = Namespace('http://www.w3.org/2004/02/skos/core#')


def standard_mode(table, metadata):
        
    FILE_URL  = Namespace(table.url + '#')
        
    g = Graph()
    g.bind('csvw', CSVW)

    tg_bn = BNode()
    t_bn = BNode()
    
    g.add((tg_bn, RDF.type, CSVW.TableGroup))
    g.add((tg_bn, CSVW.table, t_bn))
    
    g.add((t_bn, CSVW.url, URIRef(table.url)))  
    g.add((t_bn, RDF.type, CSVW.Table))

    for s,p,o in metadata.triples( (None,  URIRef('http://www.w3.org/ns/csvw#column'), None) ):
        collection_resource = metadata.value(s, URIRef('http://www.w3.org/ns/csvw#column'))
        collection = Collection(metadata, collection_resource)

    for row in table.rows:
        
        r_bn = BNode()
        rd_bn = BNode()
        
        g.add((t_bn, CSVW.row, r_bn))
        g.add((r_bn, RDF.type, CSVW.Row))
        g.add((r_bn, CSVW.rownum, Literal(row.number, datatype=XSD.integer)))
        g.add((r_bn, CSVW.describes, rd_bn))
        g.add((r_bn, CSVW.url, FILE_URL['row=' + str(row.number + 1)]))


        for cell in row.cells:
             
            if cell.value != "": 
                
                index = int(str(cell.column)[-1:]) - 1 
                column_name = metadata.value(collection[index], URIRef('http://www.w3.org/ns/csvw#title'))
                
                iri = iribaker.to_iri(FILE_URL[column_name])
                
                try:
                    g.add((rd_bn, iri, Literal(cell.value)))
                
                except Exception: 
                    print "Exception!"
                    print column_name 
                    print iri
                    print FILE_URL[column_name]
                    traceback.print_exc(file=sys.stdout)
                    print
        
    return g
