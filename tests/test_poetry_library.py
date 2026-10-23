"""Corpus query/adapter regressions. Fixtures are synthetic, not attributed poems.

Run with the optional corpus venv to exercise simplification and SQL integration.
Without OpenCC the pure adapter tests run and integration cases explicitly skip.
"""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import poetry_library as lib


class TestSourceAdapters(unittest.TestCase):
    def test_body_variants_preserve_original_text(self):
        for field, body, expected in [("paragraphs", ["繁體原文。"], ["繁體原文。"]),
                                      ("para", ["第一行", "第二行"], ["第一行", "第二行"]),
                                      ("content", "一則短文", ["一則短文"])]:
            with self.subTest(field=field):
                row = next(lib.iter_entries({field: body}))
                self.assertEqual(row["paragraphs"], expected)

    def test_compiler_not_inherited_as_embedded_poem_author(self):
        data = {"title": "测试选集", "author": "编者甲", "content": [
            {"title": "测试篇", "paragraphs": ["测试正文"]},
        ]}
        row = next(lib.iter_entries(data))
        self.assertEqual(row["author"], "")
        self.assertEqual(row["context"], ["测试选集"])
        self.assertEqual(row["source_pointer"], "/content/0")

    def test_author_of_explicit_work_group_is_preserved(self):
        data = {"chapter": "组诗", "author": "作者甲", "paragraphs": [
            {"subchapter": "其一", "paragraphs": ["第一首"]},
            {"subchapter": "其二", "paragraphs": ["第二首"]},
        ]}
        rows = list(lib.iter_entries(data))
        self.assertEqual([row["author"] for row in rows], ["作者甲", "作者甲"])
        self.assertEqual(rows[1]["source_pointer"], "/paragraphs/1")

    def test_notes_and_biographies_are_not_new_works(self):
        data = {"paragraphs": ["正文"], "notes": ["注释"], "biography": "简介"}
        rows = list(lib.iter_entries(data))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["paragraphs"], ["正文"])
        self.assertEqual(rows[0]["notes"], ["注释"])

    def test_empty_body_is_explicitly_recorded(self):
        row = next(lib.iter_entries([{"title": "空条目", "paragraphs": []}]))
        self.assertEqual(row, {"source_pointer": "/0", "skip_reason": "empty_text"})

    def test_unknown_shape_is_not_silently_dropped(self):
        with self.assertRaises(lib.LibraryError):
            list(lib.iter_entries({"title": "只有题目"}))

    def test_json_pointer_recovers_original_nested_record(self):
        data = {"title": "书", "content": [{"chapter": "卷", "content": [
            {"title": "篇", "content": ["原文"]},
        ]}]}
        row = next(lib.iter_entries(data))
        recovered = data
        for token in row["source_pointer"].split("/")[1:]:
            recovered = recovered[int(token)] if isinstance(recovered, list) else recovered[token]
        self.assertEqual(recovered["content"], row["paragraphs"])

    def test_missing_database_is_not_a_valid_zero_result(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                code = lib.main(["--home", directory, "--json", "status"])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")


@unittest.skipUnless(importlib.util.find_spec("opencc"), "optional corpus OpenCC dependency is not installed")
class TestLibraryQueries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        self.normalizer = lib.Normalizer()
        self.poems = self.source / "诗.json"
        self.poems.write_text(json.dumps([
            {"author": "測試甲", "title": "夢中消息", "paragraphs": ["明月與夢。", "原文第二行。"], "notes": ["只有注释中的检索词"]},
            {"author": "測試甲乙", "title": "另一篇", "paragraphs": ["明月在別處。"]},
            {"author": "測試甲", "title": "符号", "paragraphs": ["百分号%和下划线_是原文。"]},
            {"author": "測試甲", "title": "缺文", "paragraphs": []},
        ], ensure_ascii=False))
        self.ci = self.source / "词.json"
        self.ci.write_text(json.dumps([{"author": "測試乙", "rhythmic": "如夢令", "paragraphs": ["夢裡的另一篇詞。"]}], ensure_ascii=False))
        self.book = self.source / "书.json"
        self.book.write_text(json.dumps({"title": "測試書", "author": "编者", "content": [
            {"chapter": "某章", "paragraphs": ["章內的正文。"]},
        ]}, ensure_ascii=False))
        self.files = [("tang", "唐", self.poems), ("song-ci", "宋", self.ci), ("mengxue", "", self.book)]
        self.path = self.home / "poetry.sqlite3"
        self.metadata = lib.build_index(self.source, self.path, lib.CORPUS_REVISION, self.normalizer, self.files)
        self.db = lib.connect_readonly(self.path)
        self.addCleanup(self.db.close)

    def query(self, **kwargs):
        return lib.search(self.db, self.metadata, self.normalizer, **kwargs)

    def test_simplified_query_returns_unmodified_traditional_original(self):
        result = self.query(author="测试甲", title="梦中", keyword=["月", "梦"])
        self.assertEqual(result["returned"], 1)
        self.assertEqual(result["results"][0]["paragraphs"], ["明月與夢。", "原文第二行。"])
        self.assertEqual(self.query(author="測試甲", title="夢中")["results"][0]["id"], result["results"][0]["id"])

    def test_author_is_exact_not_prefix_match(self):
        self.assertEqual(self.query(author="测试甲", count=True)["total_matches"], 2)

    def test_cipai_is_not_fabricated_as_title(self):
        result = self.query(rhythmic="如梦令")
        self.assertEqual(result["results"][0]["title"], "")
        self.assertEqual(self.query(title="如梦令")["returned"], 0)

    def test_nested_chapter_can_be_found_through_book_title(self):
        result = self.query(title="测试书")
        self.assertEqual(result["results"][0]["title"], "某章")
        self.assertEqual(result["results"][0]["author"], "")

    def test_keywords_search_body_not_notes(self):
        self.assertEqual(self.query(keyword=["只有注释中的检索词"])["returned"], 0)

    def test_percent_underscore_and_sql_text_are_literals(self):
        self.assertEqual(self.query(keyword=["%"])["returned"], 1)
        self.assertEqual(self.query(keyword=["_"])["returned"], 1)
        self.assertEqual(self.query(author="' OR 1=1 --")["returned"], 0)

    def test_pagination_never_claims_page_size_is_total(self):
        first = self.query(author="测试甲", limit=1)
        second = self.query(author="测试甲", limit=1, offset=1, count=True)
        self.assertIsNone(first["total_matches"])
        self.assertTrue(first["has_more"])
        self.assertFalse(second["has_more"])
        self.assertEqual(second["total_matches"], 2)
        self.assertNotEqual(first["results"][0]["id"], second["results"][0]["id"])

    def test_provenance_identifies_file_record_and_revision(self):
        row = self.query(title="梦中")["results"][0]
        self.assertEqual(row["source_file"], "诗.json")
        self.assertEqual(row["source_pointer"], "/0")
        self.assertIn(lib.CORPUS_REVISION, row["source_url"])

    def test_empty_records_are_counted_separately(self):
        self.assertEqual(self.metadata["total_records"], 5)
        self.assertEqual(len(self.metadata["skipped_records"]), 1)

    def test_queries_are_readonly(self):
        with self.assertRaises(sqlite3.OperationalError):
            self.db.execute("DELETE FROM works")

    def test_rebuild_failure_preserves_previous_index_and_sources(self):
        self.db.close()
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        original = self.poems.read_bytes()
        self.book.write_text('{"unsupported": true}')
        with self.assertRaises(lib.LibraryError):
            lib.build_index(self.source, self.path, lib.CORPUS_REVISION, self.normalizer, self.files)
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)
        self.assertEqual(self.poems.read_bytes(), original)
        self.assertEqual(list(self.home.glob("poetry-index-*.sqlite3")), [])

    def test_unknown_index_is_not_overwritten(self):
        foreign = self.home / "other.sqlite3"
        foreign.write_text("user data")
        with self.assertRaises(lib.LibraryError):
            lib.build_index(self.source, foreign, lib.CORPUS_REVISION, self.normalizer, self.files)
        self.assertEqual(foreign.read_text(), "user data")

    def test_index_normalizer_change_is_not_treated_as_no_matches(self):
        self.db.close()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE metadata SET value = ? WHERE key = 'normalizer'", (json.dumps("different normalizer"),))
        with self.assertRaises(lib.LibraryError):
            lib.connect_readonly(self.path)

    def test_incomplete_metadata_is_explicit_error_not_empty_library(self):
        self.db.close()
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM metadata WHERE key = 'revision'")
        output = io.StringIO()
        with redirect_stdout(output):
            code = lib.main(["--home", str(self.home), "--json", "status"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
