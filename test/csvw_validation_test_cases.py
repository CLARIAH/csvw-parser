import urlparse
import traceback
import unittest
import json
from StringIO import StringIO
from csvwparser import CSVW, metadata
import urllib2

MAX_TESTS = 20
MANIFEST = 'http://w3c.github.io/csvw/tests/manifest-validation.jsonld'
BASE = 'http://w3c.github.io/csvw/tests/'
TYPES = {
    'csvt:WarningValidationTest': True,
    'csvt:PositiveValidationTest': True,
    'csvt:NegativeValidationTest': False
}


def get_manifest():
    response = urllib2.urlopen(MANIFEST)
    return json.loads(response.read())


class CSVWValidationTestCases(unittest.TestCase):
    def test(self):
        url = 'http://w3c.github.io/csvw/tests/test011/tree-ops.csv'

        csvw = CSVW(url=url)

        # if we can parse it we should at least produce a table and some embedded metadata
        self.assertNotEqual(csvw.table, None)
        self.assertNotEqual(csvw.metadata, None)

        result_table = csvw.table
        result_meta = csvw.metadata.json()


def test_generator(csv_url, implicit, type, option):
    def test(self):
        metadata = option.get('metadata')

        try:
            csvw = CSVW(url=csv_url, metadata_url=metadata)
        except Exception as e:
            # this should be a negative test
            if TYPES[type]:
                traceback.print_exc()
            self.assertFalse(TYPES[type])
            return

        # if we get here this should be a positive test
        self.assertTrue(TYPES[type])

        # if we can parse it we should at least produce a table and some embedded metadata
        self.assertNotEqual(csvw.table, None)
        self.assertNotEqual(csvw.metadata, None)

        result_table = csvw.table
        result_meta = csvw.metadata.json()

    return test

def test_generator_metadata(metadata_url, implicit, type, option):
    def test(self):
        metadata_provided = option.get('metadata')

        url_resp = urllib2.urlopen(metadata_url)
        handle = StringIO(url_resp.read())
        meta = json.load(handle)

        meta_model = metadata.normalize(meta)

        self.assertNotEqual(meta_model, None)
    return test


if __name__ == '__main__':
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        test_name = 'test ' + t['type'] + ': ' + t['name']
        action_url = t['action']
        action_url = urlparse.urljoin(BASE, action_url)
        implicit = []
        if 'implicit' in t:
            for f in t['implicit']:
                implicit.append(urlparse.urljoin(BASE, f))

        if 'metadata' in t['option']:
            t['option']['metadata'] = urlparse.urljoin(BASE, t['option']['metadata'])

        if action_url.endswith('.csv'):
            test = test_generator(action_url, implicit, t['type'], t['option'])
            setattr(CSVWValidationTestCases, test_name, test)
        elif action_url.endswith('.json'):
            test = test_generator_metadata(action_url, implicit, t['type'], t['option'])
            setattr(CSVWValidationTestCases, test_name, test)

        if i > MAX_TESTS:
            break

    unittest.main()