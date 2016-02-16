import unittest
import urlparse
from csvw_rdf_test_cases import get_manifest, BASE, test_generator, CSVWRDFTestCases

__author__ = 'sebastian'

if __name__ == '__main__':
    test_no = input('Test No.: ')
    test_id = '#test' + str(test_no).zfill(3)
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        
         if t['id'].endswith(test_id):
        
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


    unittest.main()

