import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(rel_path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class HelperTests(unittest.TestCase):
    def test_log_redaction(self):
        module = load_module('.github/skills/log-analyzer/scripts/redact_logs.py', 'redact_logs')
        source = 'Authorization: Bearer abcdefghijkl\npassword=verysecret\nclient_secret=\"quotedsecret\"\nnormal message\n'
        result = module.redact(source)
        self.assertNotIn('abcdefghijkl', result)
        self.assertNotIn('verysecret', result)
        self.assertNotIn('quotedsecret', result)
        self.assertIn('normal message', result)

    def test_log_summary_groups_repeated_patterns(self):
        module = load_module('.github/skills/log-analyzer/scripts/summarize_logs.py', 'summarize_logs')
        report = module.summarize('2026-10-30T10:00:00 INFO service - request id 123456\n2026-10-30T10:01:00 INFO service - request id 654321\nERROR com.example.OrderException: failed\n')
        self.assertIn('INFO: 2', report)
        self.assertIn('OrderException: 1', report)
        self.assertIn('2x', report)

    def test_openapi_conversion(self):
        module = load_module('.github/skills/occ-postman-generator/scripts/openapi_to_postman.py', 'openapi_to_postman')
        spec = {
            'openapi': '3.0.3',
            'info': {'title': 'Sample OCC API'},
            'servers': [{'url': 'https://example.test/occ/v2/{baseSite}', 'variables': {'baseSite': {'default': 'electronics'}}}],
            'paths': {'/products/{code}': {'get': {'tags': ['Products'], 'summary': 'Get product', 'parameters': [{'name': 'code', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}, {'name': 'fields', 'in': 'query', 'schema': {'type': 'string', 'default': 'BASIC'}}]}}}
        }
        collection = module.convert(spec)
        self.assertEqual(collection['info']['name'], 'Sample OCC API')
        request = collection['item'][0]['item'][0]['request']
        self.assertEqual(request['method'], 'GET')
        self.assertIn('{{baseUrl}}', request['url']['raw'])
        self.assertIn(':code', request['url']['raw'])
        self.assertEqual(collection['variable'][0]['value'], 'https://example.test/occ/v2/electronics')
        self.assertEqual(request['url']['query'][0]['value'], 'BASIC')
        self.assertFalse(request['url']['query'][0]['disabled'])

    def test_manifest_sources_exist(self):
        manifest = json.loads((ROOT / 'manifest/features.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['features']), 8)
        for feature in manifest['features'].values():
            for entry in feature['files']:
                self.assertTrue((ROOT / entry['source']).exists(), entry['source'])

if __name__ == '__main__':
    unittest.main()
