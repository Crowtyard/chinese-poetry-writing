"""Read-only literary queries over a separately installed chinese-poetry corpus.

The index stores original text alongside OpenCC-normalized search fields.
It is a source library, not a rhyme dictionary or a trained generation model.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
from urllib.parse import quote


CORPUS_URL = "https://github.com/chinese-poetry/chinese-poetry"
CORPUS_REVISION = "b8594f81a89752241442f2ce267d6f66f96704ee"
SCHEMA_VERSION = 1
NORMALIZER_VERSION = "0.1.7"
INDEX_KIND = "chinese-poetry-writing-library"
# Explicit source selection avoids indexing popularity scores, tonal annotations,
# author metadata, or alternate anthologies as if they were new poems.
COLLECTIONS = {
    "tang": ("唐诗", "唐", "全唐诗/poet.tang.*.json"),
    "song-poetry": ("宋诗", "宋", "全唐诗/poet.song.*.json"),
    "song-ci": ("宋词", "宋", "宋词/ci.song.*.json"),
    "yuanqu": ("元曲", "元", "元曲/yuanqu.json"),
    "shijing": ("诗经", "", "诗经/shijing.json"),
    "chuci": ("楚辞", "", "楚辞/chuci.json"),
    "lunyu": ("论语", "", "论语/lunyu.json"),
    "classics": ("四书五经", "", "四书五经/*.json"),
    "huajianji": ("花间集", "", "五代诗词/huajianji/*.json"),
    "nantang": ("南唐二主词", "", "五代诗词/nantang/poetrys.json"),
    "nalan": ("纳兰性德诗集", "清", "纳兰性德/纳兰性德诗集.json"),
    "caocao": ("曹操诗集", "", "曹操诗集/caocao.json"),
    "youmengying": ("幽梦影", "清", "幽梦影/youmengying.json"),
    "mengxue": ("蒙学", "", "蒙学/*.json"),
}
AUTHOR_FILES = ("全唐诗/authors.tang.json", "全唐诗/authors.song.json", "宋词/author.song.json")


class LibraryError(Exception):
    pass


def default_home():
    default = (Path("/workspace/shared/poetry-tools/corpus") if Path("/workspace").is_dir()
               else Path.home() / ".local/share/chinese-poetry-writing/corpus")
    return Path(os.environ.get("POETRY_CORPUS_HOME", default)).expanduser()


class Normalizer:
    def __init__(self):
        try:
            from opencc import OpenCC
            version = importlib.metadata.version("opencc-python-reimplemented")
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            raise LibraryError("缺少可选 OpenCC 依赖；先运行 scripts/setup_poetry_library.py。") from exc
        if version != NORMALIZER_VERSION:
            raise LibraryError(f"需要 opencc-python-reimplemented=={NORMALIZER_VERSION}，请用语料工具虚拟环境运行。")
        self.converter = OpenCC("t2s")

    def text(self, value):
        return self.converter.convert(unicodedata.normalize("NFKC", value))

    @lru_cache(maxsize=8192)
    def label(self, value):
        return self.text(value)


def git_output(source, *args):
    try:
        return subprocess.check_output(["git", "-C", str(source), *args],
                                       text=True, encoding="utf-8", stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LibraryError("无法读取语料 Git 状态；请使用完整、可信的 chinese-poetry 检出。") from exc


def verify_source(source):
    source = source.resolve()
    if not source.is_dir():
        raise LibraryError("语料尚未安装；运行 scripts/setup_poetry_library.py。")
    if Path(git_output(source, "rev-parse", "--show-toplevel")).resolve() != source:
        raise LibraryError("语料路径不是独立 Git 根目录。")
    origin = git_output(source, "remote", "get-url", "origin").rstrip("/").removesuffix(".git")
    if origin != CORPUS_URL:
        raise LibraryError("语料来源与预期不符；未覆盖已有文件。")
    revision = git_output(source, "rev-parse", "HEAD")
    if revision != CORPUS_REVISION or git_output(source, "status", "--porcelain", "--untracked-files=all"):
        raise LibraryError("语料版本不同或存在本地更改；未重置，请使用新的 --home 安装。")
    if not (source / "LICENSE").is_file():
        raise LibraryError("语料缺少原始 LICENSE。")
    return revision


def string_field(record, key):
    value = record.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise LibraryError(f"字段 {key} 不是字符串，不能猜测文集结构。")
    return value


def iter_entries(node, pointer="", context=(), grouped_author=""):
    """Adapt text records and nested book chapters, excluding notes/biographies.

    A JSON Pointer accompanies each source record. Compiler names are never
    inherited as the author of embedded works.
    """
    if isinstance(node, list):
        for i, child in enumerate(node):
            if not isinstance(child, (dict, list)):
                raise LibraryError(f"{pointer}/{i}: 预期作品或章节对象。")
            yield from iter_entries(child, f"{pointer}/{i}", context, grouped_author)
        return
    if not isinstance(node, dict):
        raise LibraryError(f"{pointer}: 无法识别作品结构。")
    title = string_field(node, "title") or string_field(node, "chapter") or string_field(node, "subchapter")
    current_context = (*context, title) if title else context
    for field in ("paragraphs", "para", "content"):
        if field not in node:
            continue
        body = node[field]
        if isinstance(body, str):
            paragraphs = [body]
        elif isinstance(body, list) and all(isinstance(x, str) for x in body):
            paragraphs = body
        elif field in ("content", "paragraphs") and isinstance(body, list):
            author = (string_field(node, "author") or grouped_author) if field == "paragraphs" else ""
            yield from iter_entries(body, f"{pointer}/{field}", current_context, author)
            return
        else:
            raise LibraryError(f"{pointer}/{field}: 未支持的正文结构。")
        if not paragraphs or not any(x.strip() for x in paragraphs):
            yield {"source_pointer": pointer, "skip_reason": "empty_text"}
            return
        notes = node.get("notes", [])
        if not isinstance(notes, list) or not all(isinstance(x, str) for x in notes):
            # Other metadata is left in the original JSON rather than coerced.
            notes = []
        yield {
            "title": title, "author": string_field(node, "author") or grouped_author,
            "author_basis": "record" if string_field(node, "author") else "work_group" if grouped_author else "unspecified",
            "rhythmic": string_field(node, "rhythmic"), "paragraphs": paragraphs,
            "context": list(context), "notes": notes, "source_pointer": pointer,
            "upstream_id": string_field(node, "id"),
        }
        return
    raise LibraryError(f"{pointer}: 未找到可识别正文；不会静默遗漏作品。")


def select_files(source):
    result = []
    for key, (_, dynasty, pattern) in COLLECTIONS.items():
        paths = sorted(source.glob(pattern))
        if not paths:
            raise LibraryError(f"缺少必需文集 {key}（{pattern}）。")
        for path in paths:
            if not path.is_file() or not path.resolve().is_relative_to(source.resolve()):
                raise LibraryError(f"语料文件不可读或越出语料根目录：{path.name}")
            result.append((key, dynasty, path))
    return result


def read_metadata(db):
    try:
        metadata = dict(db.execute("SELECT key, value FROM metadata"))
        if metadata.get("kind") != INDEX_KIND or int(metadata.get("schema_version", 0)) != SCHEMA_VERSION:
            raise LibraryError("索引类型或版本不兼容；请重新建立独立索引。")
        decoded = {key: json.loads(value) for key, value in metadata.items() if key not in ("kind", "schema_version")}
        required = {"source", "source_root", "revision", "normalizer", "counts", "total_records", "source_hashes", "skipped_records", "scope"}
        if not required.issubset(decoded):
            raise LibraryError("索引元数据不完整，不能作为有效原文库使用。")
        if (decoded["source"] != CORPUS_URL or not isinstance(decoded["source_root"], str)
                or not isinstance(decoded["revision"], str) or not isinstance(decoded["counts"], dict)
                or not isinstance(decoded["total_records"], int) or decoded["total_records"] < 0
                or not all(isinstance(n, int) and n >= 0 for n in decoded["counts"].values())
                or sum(decoded["counts"].values()) != decoded["total_records"]
                or not isinstance(decoded["source_hashes"], dict) or not isinstance(decoded["skipped_records"], list)):
            raise LibraryError("索引来源或数量元数据无效，请检查后重建。")
        expected = f"opencc-python-reimplemented/{NORMALIZER_VERSION}/t2s/NFKC"
        if decoded.get("normalizer") != expected:
            raise LibraryError("索引的简繁归一化规则不兼容；请重建索引，不能当成查询无结果。")
        return decoded
    except (sqlite3.Error, ValueError) as exc:
        raise LibraryError("索引损坏或不兼容，未把查询结果当成空库。") from exc


def connect_readonly(path):
    if not path.is_file():
        raise LibraryError("本地索引尚未建立；运行 scripts/setup_poetry_library.py。")
    db = None
    try:
        db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        read_metadata(db)
        return db
    except (sqlite3.Error, LibraryError) as exc:
        if db is not None:
            db.close()
        if isinstance(exc, LibraryError):
            raise
        raise LibraryError("无法打开只读索引。") from exc


def build_index(source, destination, revision, normalizer, files=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        existing = connect_readonly(destination)
        existing.close()  # Only replace an index owned by this application.
    files = select_files(source) if files is None else files
    fd, temporary = tempfile.mkstemp(prefix="poetry-index-", suffix=".sqlite3", dir=destination.parent)
    os.close(fd)
    counts = Counter()
    skipped_records = []
    file_hashes = {}
    db = None
    try:
        db = sqlite3.connect(temporary)
        db.executescript("""
          CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
          CREATE TABLE works (
            id TEXT PRIMARY KEY, collection TEXT NOT NULL, dynasty TEXT NOT NULL,
            author TEXT NOT NULL, title TEXT NOT NULL, rhythmic TEXT NOT NULL,
            paragraphs TEXT NOT NULL, context TEXT NOT NULL, notes TEXT NOT NULL,
            source_file TEXT NOT NULL, source_pointer TEXT NOT NULL, upstream_id TEXT NOT NULL,
            author_key TEXT NOT NULL, title_key TEXT NOT NULL,
            rhythmic_key TEXT NOT NULL, body_key TEXT NOT NULL,
            context_key TEXT NOT NULL, author_basis TEXT NOT NULL);
          CREATE TABLE authors (name TEXT, name_key TEXT, description TEXT,
                                source_file TEXT, source_pointer TEXT);
        """)
        for file_number, (collection, dynasty, path) in enumerate(files):
            relative = path.relative_to(source).as_posix()
            raw = path.read_bytes()
            file_hashes[relative] = hashlib.sha256(raw).hexdigest()
            try:
                data = json.loads(raw.decode("utf-8-sig"))
                for entry in iter_entries(data):
                    pointer = entry["source_pointer"]
                    if "skip_reason" in entry:
                        skipped_records.append({"source_file": relative, "source_pointer": pointer,
                                                "reason": entry["skip_reason"]})
                        continue
                    if not entry["author"] and collection in ("caocao", "youmengying"):
                        entry["author"] = {"caocao": "曹操", "youmengying": "张潮"}[collection]
                        entry["author_basis"] = "collection"
                    identity = hashlib.sha256(f"{collection}\0{relative}\0{pointer}".encode()).hexdigest()[:24]
                    body = "\n".join(entry["paragraphs"])
                    db.execute("INSERT INTO works VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                        identity, collection, dynasty, entry["author"], entry["title"], entry["rhythmic"],
                        json.dumps(entry["paragraphs"], ensure_ascii=False),
                        json.dumps(entry["context"], ensure_ascii=False),
                        json.dumps(entry["notes"], ensure_ascii=False), relative, pointer, entry["upstream_id"],
                        normalizer.label(entry["author"]), normalizer.label(entry["title"]),
                        normalizer.label(entry["rhythmic"]), normalizer.text(body),
                        normalizer.label(" / ".join(entry["context"])), entry["author_basis"],
                    ))
                    counts[collection] += 1
            except (ValueError, UnicodeError, LibraryError) as exc:
                raise LibraryError(f"{relative}: {exc}") from exc
            if file_number % 50 == 0:
                print(f"索引 {file_number + 1}/{len(files)} 文件，已收录 {sum(counts.values())} 条", file=sys.stderr, flush=True)
        for relative in AUTHOR_FILES:
            path = source / relative
            if not path.is_file():
                continue
            raw = path.read_bytes()
            file_hashes[relative] = hashlib.sha256(raw).hexdigest()
            for i, row in enumerate(json.loads(raw.decode("utf-8-sig"))):
                name = string_field(row, "name")
                description = string_field(row, "desc") or string_field(row, "description")
                db.execute("INSERT INTO authors VALUES (?,?,?,?,?)", (
                    name, normalizer.label(name), description, relative, f"/{i}",
                ))
        metadata = {
            "source": CORPUS_URL, "source_root": str(source.resolve()), "revision": revision,
            "normalizer": f"opencc-python-reimplemented/{NORMALIZER_VERSION}/t2s/NFKC",
            "counts": dict(counts), "total_records": sum(counts.values()),
            "skipped_records": skipped_records,
            "source_hashes": file_hashes,
            "scope": "14 selected collections; alternate editions/rank/strains excluded",
        }
        db.executemany("INSERT INTO metadata VALUES (?,?)", [("kind", INDEX_KIND), ("schema_version", str(SCHEMA_VERSION))])
        db.executemany("INSERT INTO metadata VALUES (?,?)", [(k, json.dumps(v, ensure_ascii=False)) for k, v in metadata.items()])
        db.executescript("""
          CREATE INDEX works_author ON works(author_key);
          CREATE INDEX works_collection ON works(collection);
          CREATE INDEX works_dynasty ON works(dynasty);
          CREATE INDEX works_rhythmic ON works(rhythmic_key);
          CREATE INDEX authors_name ON authors(name_key);
        """)
        db.commit()
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise LibraryError("新索引完整性检查失败，保留旧索引。")
        db.close()
        db = None
        os.replace(temporary, destination)
        return metadata
    finally:
        if db is not None:
            db.close()
        Path(temporary).unlink(missing_ok=True)


def source_url(revision, relative):
    return f"{CORPUS_URL}/blob/{revision}/{quote(relative, safe='/')}"


def display_record(row, metadata):
    result = {key: row[key] for key in ("id", "collection", "dynasty", "author", "author_basis", "title", "rhythmic", "source_file", "source_pointer", "upstream_id")}
    result.update({key: json.loads(row[key]) for key in ("paragraphs", "context", "notes")})
    result["source_url"] = source_url(metadata["revision"], row["source_file"])
    return result


def search(db, metadata, normalizer, *, author=None, title=None, keyword=(), collection=None,
           dynasty=None, rhythmic=None, limit=10, offset=0, count=False, exact_title=False):
    if not 1 <= limit <= 50 or offset < 0:
        raise LibraryError("limit 必须为 1–50，offset 不能为负数。")
    clauses, parameters = [], []
    for column, value in (("author_key", author), ("rhythmic_key", rhythmic),
                          ("collection", collection), ("dynasty", dynasty)):
        if value is not None:
            clauses.append(f"{column} = ?")
            parameters.append(normalizer.label(value) if column.endswith("_key") else value)
    if title is not None:
        clauses.append("title_key = ?" if exact_title else "(instr(title_key, ?) > 0 OR instr(context_key, ?) > 0)")
        parameters.extend([normalizer.label(title)] * (1 if exact_title else 2))
    for word in keyword:
        if not word.strip():
            raise LibraryError("关键词不能为空。")
        clauses.append("instr(body_key, ?) > 0")
        parameters.append(normalizer.text(word))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    rows = list(db.execute("SELECT * FROM works" + where + " ORDER BY collection, source_file, source_pointer LIMIT ? OFFSET ?",
                           (*parameters, limit + 1, offset)))
    total = db.execute("SELECT count(*) FROM works" + where, parameters).fetchone()[0] if count else None
    return {
        "status": "OK", "mode": "literal_search", "total_matches": total,
        "returned": min(len(rows), limit), "has_more": len(rows) > limit, "offset": offset,
        "results": [display_record(row, metadata) for row in rows[:limit]],
    }


def create_parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--home", type=Path, default=default_home())
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="从固定版本原文重建索引，成功后原子替换")
    index.add_argument("--source", type=Path)
    sub.add_parser("status", help="显示索引覆盖范围、数量与版本")
    find = sub.add_parser("search", help="按真实字段和正文子串组合查询")
    find.add_argument("--author")
    find.add_argument("--title")
    find.add_argument("--exact-title", action="store_true")
    find.add_argument("--keyword", action="append", default=[])
    find.add_argument("--collection", choices=list(COLLECTIONS))
    find.add_argument("--dynasty")
    find.add_argument("--rhythmic", help="确切词牌，不当成作品题名")
    find.add_argument("--limit", type=int, default=10)
    find.add_argument("--offset", type=int, default=0)
    find.add_argument("--count", action="store_true")
    sub.add_parser("show", help="以索引 id 读取完整原文").add_argument("id")
    sub.add_parser("author", help="查原库作者简介及库内作品数量").add_argument("name")
    return ap


def run(args):
    home = args.home.expanduser().resolve()
    path = home / "poetry.sqlite3"
    if args.command == "index":
        source = (args.source or home / "chinese-poetry").resolve()
        metadata = build_index(source, path, verify_source(source), Normalizer())
        return {"status": "OK", "total_records": metadata["total_records"], "counts": metadata["counts"],
                "skipped_empty_records": len(metadata["skipped_records"]), "revision": metadata["revision"]}
    db = connect_readonly(path)
    try:
        metadata = read_metadata(db)
        if metadata["revision"] != CORPUS_REVISION:
            raise LibraryError("语料索引版本与工具不匹配，请重新安装到新目录。")
        if args.command == "status":
            return {"status": "OK", **{k: v for k, v in metadata.items() if k != "source_hashes"}}
        normalizer = Normalizer()
        if args.command == "search":
            result = search(db, metadata, normalizer, **{k: getattr(args, k) for k in
                            ("author", "title", "keyword", "collection", "dynasty", "rhythmic", "limit", "offset", "count", "exact_title")})
        elif args.command == "show":
            row = db.execute("SELECT * FROM works WHERE id = ?", (args.id,)).fetchone()
            result = {"status": "OK" if row else "NOT_FOUND", "results": [display_record(row, metadata)] if row else []}
        else:
            key = normalizer.label(args.name)
            biographies = [dict(row) for row in db.execute("SELECT name,description,source_file,source_pointer FROM authors WHERE name_key = ?", (key,))]
            for row in biographies:
                row["source_url"] = source_url(metadata["revision"], row["source_file"])
            counts = [dict(row) for row in db.execute("SELECT collection, count(*) AS records FROM works WHERE author_key = ? GROUP BY collection", (key,))]
            result = {"status": "OK" if biographies or counts else "NOT_FOUND", "name": args.name, "biographies": biographies, "corpus_counts": counts}
        return {"source": CORPUS_URL, "revision": metadata["revision"], **result}
    finally:
        db.close()


def ensure_optional_python(home):
    """Use the optional corpus venv when invoked with the system Python."""
    try:
        import opencc  # noqa: F401
        if importlib.metadata.version("opencc-python-reimplemented") == NORMALIZER_VERSION:
            return
    except (ImportError, importlib.metadata.PackageNotFoundError):
        pass
    python = home / "venv/bin/python"
    if python.is_file() and python.absolute() != Path(sys.executable).absolute():
        os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])


def main(argv=None):
    args = create_parser().parse_args(argv)
    try:
        # Tests pass an explicit argv and use their own interpreter/dependency.
        if argv is None and args.command != "status":
            ensure_optional_python(args.home.expanduser().resolve())
        result = run(args)
    except (LibraryError, OSError, sqlite3.Error, ValueError) as exc:
        result = {"status": "ERROR", "message": str(exc)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"本地诗词库：{result['status']}")
        if "results" in result:
            for record in result["results"]:
                heading = record["title"] or record["rhythmic"] or "（原库无题名）"
                print(f"\n《{heading}》 {record['author'] or '（原库未署名）'} [{record['collection']}]")
                print("\n".join(record["paragraphs"]))
                print(f"来源：{record['source_url']} JSON Pointer={record['source_pointer'] or '/'}")
                print(f"索引 id：{record['id']}")
            if "returned" in result:
                print(f"\n本页 {result['returned']} 条；总数：{result['total_matches'] if result['total_matches'] is not None else '未统计'}；还有更多：{result['has_more']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
