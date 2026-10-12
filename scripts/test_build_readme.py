"""Regression checks for bilingual publication boundaries."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
import build_readme as builder


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()
        self.patch = patch.object(builder, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.doc = {
            'section': 'Data', 'section_zh': '数据', 'order': 10,
            'description': 'Record demonstrations.', 'description_zh': '录制示教。',
            'entries': [{
                'id': 'example', 'name': 'Example project',
                'url': 'https://example.org', 'type': 'docs', 'maturity': 'research',
                'what': 'A data guide.', 'what_zh': '数据指南。',
            }],
        }

    def write(self, doc=None, filename='data.yaml'):
        (self.root / 'data' / filename).write_text(
            yaml.safe_dump(self.doc if doc is None else doc, allow_unicode=True)
        )

    def test_missing_translation_fails_instead_of_falling_back(self):
        del self.doc['entries'][0]['what_zh']
        self.write()
        with self.assertRaisesRegex(ValueError, 'Missing zh field what'):
            builder.load()

    def test_use_conditions_require_both_languages(self):
        self.doc['entries'][0]['notes'] = 'Requires a compatible checkpoint.'
        self.write()
        with self.assertRaisesRegex(ValueError, 'Missing zh field notes'):
            builder.load()

    def test_selection_rationale_is_rejected_as_public_data(self):
        self.doc['entries'][0]['why'] = 'Internal selection decision.'
        self.write()
        with self.assertRaisesRegex(ValueError, 'editorial'):
            builder.load()

    def test_editorial_archive_is_not_a_publishing_input(self):
        self.write()
        archive = self.root / 'editorial' / 'archive' / 'data'
        archive.mkdir(parents=True)
        (archive / 'invalid.yaml').write_text('This is not public YAML content')
        docs = builder.load()
        for lang in ('zh', 'en'):
            text = builder.build_catalog(docs, lang)
            self.assertIn('<a id="example"></a>', text)
            self.assertNotIn('not public', text)

    def test_duplicate_ids_cannot_create_ambiguous_navigation(self):
        self.write()
        second = copy.deepcopy(self.doc)
        self.write(second, 'another.yaml')
        with self.assertRaisesRegex(ValueError, 'Duplicate ID'):
            builder.load()

    def test_secondary_language_changes_are_detected_as_stale(self):
        self.write()
        self.doc['symptoms'] = [{
            'id': 'sample-symptom', 'symptom': 'A stall', 'symptom_zh': '停顿',
            'causes': [{'cause': 'A delay', 'cause_zh': '延迟',
                        'test': 'Measure timing', 'test_zh': '测量时序',
                        'fix': 'Adjust scheduling', 'fix_zh': '调整调度'}],
        }]
        self.write()
        templates = self.root / 'templates'
        templates.mkdir()
        for suffix in ('', '.en'):
            (templates / f'README.head{suffix}.md').write_text('# {{TOTAL}} resources\n')
            (templates / f'README.foot{suffix}.md').write_text('License\n')
        with patch('sys.argv', ['build_readme.py']):
            self.assertEqual(builder.main(), 0)
        with patch('sys.argv', ['build_readme.py', '--check']):
            self.assertEqual(builder.main(), 0)
            target = self.root / 'docs' / 'zh' / 'resources.md'
            target.write_text(target.read_text() + '\nUnbuilt edit\n')
            self.assertEqual(builder.main(), 1)


if __name__ == '__main__':
    unittest.main()
