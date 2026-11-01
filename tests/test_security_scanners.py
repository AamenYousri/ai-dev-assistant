import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('security_scanners', ROOT / '.github/skills/security-checks/scripts/run_scanners.py')
scanners = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanners)


class SecurityScannerTests(unittest.TestCase):
    def test_secret_values_are_masked(self):
        text = 'Authorization: Bearer abcdef password=verysecret ghp_123456789012345678901234'
        masked = scanners.mask_text(text)
        self.assertNotIn('abcdef', masked)
        self.assertNotIn('verysecret', masked)
        self.assertNotIn('ghp_123456789012345678901234', masked)

    def test_version_parsing_and_incompatible_gitleaks(self):
        self.assertEqual(scanners.parse_version('gitleaks version 8.20.1'), (8, 20, 1))
        with patch.object(scanners.shutil, 'which', side_effect=lambda name: '/tools/gitleaks' if name == 'gitleaks' else None), \
             patch.object(scanners, 'command_version', return_value=('gitleaks version 8.10.0', None)):
            result = scanners.discover_scanners()
        self.assertEqual(result['gitleaks']['status'], 'incompatible')
        self.assertIn('8.19', result['gitleaks']['reason'])

    def test_missing_scanners_are_reported_without_installing(self):
        with patch.object(scanners.shutil, 'which', return_value=None):
            result = scanners.discover_scanners()
        self.assertTrue(all(info['status'] == 'missing' for info in result.values()))
        self.assertFalse(hasattr(scanners, 'install_semgrep'))

    def test_invalid_or_incomplete_json_report_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.json'
            path.write_text('{"results":', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid or incomplete JSON'):
                scanners.load_report(path, dict)
            path.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing its results'):
                scanners.semgrep_findings(scanners.load_report(path, dict))
            with self.assertRaisesRegex(ValueError, 'malformed result entry'):
                scanners.semgrep_findings({'results': [None]})

    def test_duplicate_cve_findings_merge_sources(self):
        first = scanners.finding('scanner A', 'A title', 'high', 'dependency', 'pkg', 'evidence', cve='CVE-2025-1234')
        second = scanners.finding('scanner B', 'Other title', 'medium', 'dependency', 'pkg', 'other evidence', cve='CVE-2025-1234')
        merged = scanners.deduplicate_findings([first, second])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['sources'], ['scanner A', 'scanner B'])

    def test_failed_process_is_not_reported_as_success(self):
        info = {'status': 'available', 'executable': 'semgrep', 'version': '1.0.0'}
        args = type('Args', (), {'allow_network': True, 'semgrep_config': 'auto', 'timeout': 1})()
        with tempfile.TemporaryDirectory() as directory, patch.object(scanners, 'run_process', return_value=RuntimeError('scanner failed')):
            result, _ = scanners.execute_scanner('semgrep', info, '.', Path(directory), args)
        self.assertEqual(result['scan_status'], 'failed')

    def test_nonzero_scanner_exit_with_valid_json_is_still_failure(self):
        info = {'status': 'available', 'executable': 'semgrep', 'version': '1.0.0'}
        args = type('Args', (), {'allow_network': True, 'semgrep_config': 'auto', 'timeout': 1})()
        with tempfile.TemporaryDirectory() as directory:
            def fake_process(command, timeout):
                output_path = Path(command[command.index('--output') + 1])
                output_path.write_text('{"results": []}', encoding='utf-8')
                return type('Result', (), {'returncode': 2})()
            with patch.object(scanners, 'run_process', side_effect=fake_process):
                result, _ = scanners.execute_scanner('semgrep', info, '.', Path(directory), args)
        self.assertEqual(result['scan_status'], 'failed')

    def test_dependency_database_update_failure_is_separate_from_scan(self):
        info = {'status': 'available', 'executable': 'dependency-check', 'version': '12.0.0', 'java_major': 17}
        args = type('Args', (), {'allow_network': True, 'semgrep_config': 'auto', 'timeout': 1})()
        with patch.object(scanners, 'run_process', return_value=type('Result', (), {'returncode': 1, 'stderr': 'update failed'})()):
            result, _ = scanners.execute_scanner('dependency-check', info, '.', Path('unused'), args)
        self.assertEqual(result['database_update'], 'failed')
        self.assertEqual(result['scan'], 'not_run')
        self.assertEqual(result['scan_status'], 'failed')

    def test_gitleaks_output_omits_secret_values(self):
        report = [{'RuleID': 'aws-access-key', 'File': 'config.env', 'StartLine': 2,
                   'Secret': 'DO_NOT_LEAK', 'Match': 'AKIA1234567890123456'}]
        serialized = json.dumps(scanners.gitleaks_findings(report, 'Gitleaks'))
        self.assertNotIn('DO_NOT_LEAK', serialized)
        self.assertNotIn('AKIA1234567890123456', serialized)
        self.assertIn('intentionally omitted', serialized)

    def test_report_draft_never_marks_unreviewed_checks_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            scanners.write_report_draft(Path(directory), {'overall': 'incomplete', 'target': '.', 'finding_count': 0, 'scanners': {}}, [])
            report = (Path(directory) / 'SECURITY_REPORT.md').read_text(encoding='utf-8')
        self.assertIn('| C01 | Authentication | NOT RUN |', report)
        self.assertIn('| B7 | Email Security | NOT RUN |', report)
        self.assertIn('No check is marked PASS', report)
        self.assertEqual(report.count('| NOT RUN | Review required |'), 34)

    def test_report_lists_scanner_failures_under_failed_checks(self):
        summary = {'overall': 'failed', 'target': '.', 'finding_count': 0,
                   'scanners': {'semgrep': {'status': 'available', 'scan_status': 'failed', 'reason': 'failed'}}}
        with tempfile.TemporaryDirectory() as directory:
            scanners.write_report_draft(Path(directory), summary, [])
            report = (Path(directory) / 'SECURITY_REPORT.md').read_text(encoding='utf-8')
        failed_section = report.split('## 9. Failed Checks', 1)[1].split('## 10.', 1)[0]
        self.assertIn('Scanner execution failed: semgrep', failed_section)

    def test_offline_dependency_database_keeps_overall_incomplete(self):
        args = type('Args', (), {'allow_network': False, 'semgrep_config': 'local-rules.yml', 'timeout': 1})()
        with tempfile.TemporaryDirectory() as directory:
            # The dependency-check scan itself must not be reported complete without a current DB.
            info = {'status': 'available', 'executable': 'dependency-check', 'version': '12.0.0', 'java_major': 17}
            with patch.object(scanners, 'run_process') as process, patch.object(scanners, 'load_report', return_value={'dependencies': []}):
                process.return_value = type('Result', (), {'returncode': 0})()
                result, _ = scanners.execute_scanner('dependency-check', info, '.', Path(directory), args)
        self.assertEqual(result['database_update'], 'not_attempted_offline')
        self.assertEqual(scanners.overall_status({'dependency-check': result}), 'incomplete')

    def test_report_orders_findings_by_severity(self):
        findings = [
            scanners.finding('test', 'Low issue', 'LOW', 'test', 'a', 'evidence'),
            scanners.finding('test', 'Critical issue', 'CRITICAL', 'test', 'b', 'evidence'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            scanners.write_report_draft(Path(directory), {'overall': 'incomplete', 'target': '.', 'finding_count': 2, 'scanners': {}}, findings)
            report = (Path(directory) / 'SECURITY_REPORT.md').read_text(encoding='utf-8')
        self.assertLess(report.index('Critical issue'), report.index('Low issue'))


if __name__ == '__main__':
    unittest.main()