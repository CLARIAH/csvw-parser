import urlparse
import traceback
import unittest
import json
from pycsvw import CSVW
import urllib2
from rdflib import Graph, compare


MAX_TESTS = 6
MANIFEST = 'http://w3c.github.io/csvw/tests/manifest-rdf.jsonld'
BASE = 'http://w3c.github.io/csvw/tests/'
TYPES = {
    'csvt:ToRdfTest': True,
    'csvt:ToRdfTestWithWarnings': True,
    'csvt:NegativeRdfTest': False
}


def get_manifest():
    response = urllib2.urlopen(MANIFEST)
    return json.loads(response.read())


class CSVWRDFTestCases(unittest.TestCase):
        pass


def test_generator(csv_file, result_url, implicit, type, option):
    
    name = csv_file.split("/")[-1][:-4] 

    
    
    def test(self):
        metadata = None
        if 'metadata' in option:
            metadata = option['metadata']

        try:
            csvw = CSVW(csv_file, metadata_url=metadata)
            
            
        except Exception as e:
            # this should be a negative test
            if TYPES[type]:
                traceback.print_exc()
            self.assertFalse(TYPES[type])
            return

        # if we get here this should be a positive test
        self.assertTrue(TYPES[type])

        # if we can parse it we should at least produce some embedded metadata
        self.assertNotEqual(csvw.metadata, None)
        # and the result should exists
        self.assertNotEqual(result_url, None)


        gr = Graph()
        result = gr.parse(result_url)
        converted_result = csvw.to_rdf()
    
        result.serialize('output/' + name + '.ttl', format='turtle')
        converted_result.serialize('output/converted_' + name + '.ttl', format='turtle')
        
        self.assertTrue(compare.isomorphic(result, converted_result))
        
    return test



if __name__ == '__main__':
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        
        test_name = 'test ' + t['type'] + ': ' + t['name']
        
        csv_file = t['action']
        
        csv_file = urlparse.urljoin(BASE, csv_file)

        result = None
        if 'result' in t:
            result = urlparse.urljoin(BASE, t['result'])

        implicit = []
        if 'implicit' in t:
            for f in t['implicit']:
                implicit.append(urlparse.urljoin(BASE, f))
                
        if 'metadata' in t['option']:
            t['option']['metadata'] = urlparse.urljoin(BASE, t['option']['metadata'])
        

        test = test_generator(csv_file, result, implicit, t['type'], t['option'])
        setattr(CSVWRDFTestCases, test_name, test)

        i += 1
        
        if i >= MAX_TESTS:
            break

    unittest.main()
