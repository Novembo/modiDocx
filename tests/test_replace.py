import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document

import replace
from replace import ReplacementRule, export_rules, import_rules, preview_documents, process_documents


class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def make_docx(self, name="sample.docx"):
        path = self.root / name
        document = Document()
        path.parent.mkdir(parents=True, exist_ok=True)
        document.save(path)
        return path

    def test_preview_and_replace_text_split_across_runs_and_header(self):
        source = self.make_docx()
        document = Document(source)
        paragraph = document.add_paragraph()
        paragraph.add_run("Bonjour ")
        paragraph.add_run("équipe")
        document.sections[0].header.paragraphs[0].text = "Bonjour équipe"
        document.save(source)

        rules = [ReplacementRule("Bonjour équipe", "Bonjour tout le monde")]
        preview = preview_documents([source], rules)
        self.assertEqual(preview[0].counts, (2,))
        result = process_documents([source], rules)[0]
        modified = Document(result.output)
        self.assertEqual(result.counts, (2,))
        self.assertEqual(modified.paragraphs[0].text, "Bonjour tout le monde")
        self.assertEqual(modified.sections[0].header.paragraphs[0].text, "Bonjour tout le monde")

    def test_column_rule_only_targets_matching_table_column(self):
        source = self.make_docx()
        document = Document(source)
        table = document.add_table(rows=2, cols=2)
        table.rows[0].cells[0].text = "Nom"
        table.rows[0].cells[1].text = "Ville"
        table.rows[1].cells[0].text = "Paris"
        table.rows[1].cells[1].text = "Paris"
        document.save(source)

        result = process_documents([source], [ReplacementRule("Paris", "Lyon", "Ville")])[0]
        table = Document(result.output).tables[0]
        self.assertEqual(result.counts, (1,))
        self.assertEqual(table.rows[1].cells[0].text, "Paris")
        self.assertEqual(table.rows[1].cells[1].text, "Lyon")

    def test_rules_json_round_trip_and_rejects_unknown_version(self):
        path = self.root / "rules.json"
        rules = [ReplacementRule("ancien", "nouveau", "Ville")]
        export_rules(path, "Équipe", rules)
        name, loaded = import_rules(path)
        self.assertEqual(name, "Équipe")
        self.assertEqual(loaded, rules)
        path.write_text(json.dumps({"version": 2, "name": "x", "rules": []}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Version"):
            import_rules(path)

    def test_invalid_input_prevents_any_batch_output(self):
        valid = self.make_docx("one.docx")
        invalid = self.root / "broken.docx"
        invalid.write_text("not a docx", encoding="utf-8")
        with self.assertRaises(Exception):
            process_documents([valid, invalid], [ReplacementRule("a", "b")])
        self.assertFalse((self.root / "one_modified.docx").exists())

    def test_staging_failure_publishes_no_partial_results(self):
        first = self.make_docx("one.docx")
        second = self.make_docx("two.docx")
        original = replace._apply_rules
        calls = 0

        def fail_on_second(document, rules):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated save preparation failure")
            return original(document, rules)

        with patch("replace._apply_rules", side_effect=fail_on_second):
            with self.assertRaisesRegex(ValueError, "simulated"):
                process_documents([first, second], [ReplacementRule("a", "b")])
        self.assertFalse((self.root / "one_modified.docx").exists())
        self.assertFalse((self.root / "two_modified.docx").exists())

    def test_existing_result_is_preserved_and_new_name_is_chosen(self):
        source = self.make_docx()
        existing = self.root / "sample_modified.docx"
        existing.write_bytes(b"keep me")
        result = process_documents([source], [ReplacementRule("a", "b")])[0]
        self.assertEqual(existing.read_bytes(), b"keep me")
        self.assertEqual(result.output.name, "sample_modified_2.docx")


if __name__ == "__main__":
    unittest.main()
