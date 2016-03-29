import urlparse
import traceback
import unittest
import json
from pycsvw import CSVW
import urllib2


from unittest import TestCase
TestCase.maxDiff = None
    
    
MAX_TESTS = 5
MANIFEST = 'http://w3c.github.io/csvw/tests/manifest-json.jsonld'
BASE = 'http://w3c.github.io/csvw/tests/'
TYPES = {
    'csvt:ToJsonTest': True,
    'csvt:ToJsonTestWithWarnings': True,
    'csvt:NegativeJsonTest': False
}


def get_manifest():
    response = urllib2.urlopen(MANIFEST)
    return json.loads(response.read())

# http://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
    
    
class CSVWJSONTestCases(unittest.TestCase):
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

        # test the json result

        resp = urllib2.urlopen(result_url)
        result = json.loads(resp.read())
        
        generated_result = json.loads(csvw.to_json())
        
        with open('output_json/' + name + '.json', 'w') as outfile:
            json.dump(result, outfile, indent=2)
            
        with open('output_json/generated_' + name + '.json', 'w') as outfile:
            json.dump(generated_result, outfile, indent=2)

        
        self.assertEqual(ordered(generated_result), ordered(result))

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
        setattr(CSVWJSONTestCases, test_name, test)

        if i > MAX_TESTS:
            break

    unittest.main()
    
