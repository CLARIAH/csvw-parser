import logging
import urllib2
import os
import simplejson
from pycsvw import metadata
from rdflib import Graph
import urllib, json
from rdflib.plugin import register, Serializer
from rdflib.graph import ConjunctiveGraph
from cStringIO import StringIO
register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')


__author__ = 'sebastian'
logger = logging.getLogger(__name__)

# 1. command-line option
# 2. metadata embedded within the tabular data file itself
# 3. metadata in a document linked to using a Link header associated with the tabular data file
HEADER_LINK = ['link', 'Link']
# 4. file-specific metadata in a document located based on the location of the tabular data file
FILE_SPECIFIC_METADATA = '-metadata.json'
# 5. directory-specific metadata in a document located based on the location of the tabular data file
DIRECTORY_METADATA = ['metadata.json', 'csv-metadata.json']


def parse_to_graph(metadata_handle):
    meta_json = simplejson.load(metadata_handle)
    # meta = metadata.validate(meta_json)

    meta_graph = ConjunctiveGraph()
    meta_graph.parse(data=json.dumps(meta_json), format='json-ld')

    return meta_graph

  
def _parse_header_field(header_field):
    raise NotImplementedError()


def metadata_graph_extraction(url, metadata_handle, embedded_metadata=False):
    meta_graph = ConjunctiveGraph()

    # case  1
    if metadata_handle is not None:
        new_graph = parse_to_graph(metadata_handle)    
        meta_graph = meta_graph + new_graph

    # case  2
    if embedded_metadata:        
        
#         print embedded_metadata
        
        new_graph = parse_to_graph(StringIO(json.dumps(embedded_metadata)))    
        meta_graph = meta_graph + new_graph


    if url:
        # case 3
        try:
            response = urllib2.urlopen(url)
            header = response.info()
            if header is not None:
                for link in HEADER_LINK:
                    if link in header:
                        header_field = header[link]
                        logger.debug('found link in http header: %s', header_field)
                        meta_graph.parse(_parse_header_field(header_field))
        except urllib2.URLError:
            pass

        # case 4
        try:
            meta_url = url + FILE_SPECIFIC_METADATA
            response = urllib2.urlopen(meta_url)
            if response.getcode() == 200:
                logger.debug('found file specific metadata: %s', meta_url)
                meta_graph.parse(parse_to_graph(response))
        except urllib2.URLError:
            pass

        # case 5
        for dir_meta in DIRECTORY_METADATA:
            try:
                # split away the part after the last slash
                directory = url.rsplit('/', 1)[-2]
                meta_url = os.path.join(directory, dir_meta)
                response = urllib2.urlopen(meta_url)
                if response.getcode() == 200:
                    logger.debug('found directory specific metadata: %s', meta_url)
                    meta_graph.parse(parse_to_graph(response))
                    break
            except urllib2.URLError:
                pass

    return meta_graph
