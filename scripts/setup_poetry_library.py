"""Prepare optional corpus checkout, isolated search dependencies and SQLite.

Retains upstream Git history/identity and LICENSE; never deletes user files or
resets an existing checkout to make it match the pinned revision.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import venv

from poetry_library import CORPUS_URL, CORPUS_REVISION, LibraryError, default_home, verify_source, connect_readonly, read_metadata, venv_python


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--home", type=Path, default=default_home())
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args(argv)
    home = args.home.expanduser().resolve()
    own_root = Path(__file__).resolve().parents[1]
    if home == own_root or own_root in home.parents:
        ap.error("数据库和依赖请放在 Skill 仓库之外。")
    home.mkdir(parents=True, exist_ok=True)
    source = home / "chinese-poetry"
    if not source.exists():
        subprocess.run(["git", "clone", "--depth", "1", CORPUS_URL + ".git", str(source)], check=True)
        # A moved upstream default branch is not silently accepted.
        current = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        if current != CORPUS_REVISION:
            subprocess.run(["git", "-C", str(source), "fetch", "--depth", "1", "origin", CORPUS_REVISION], check=True)
            subprocess.run(["git", "-C", str(source), "checkout", "--detach", CORPUS_REVISION], check=True)
    verify_source(source)
    environment = home / "venv"
    if not environment.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    python = venv_python(environment)
    if not python.is_file():
        raise LibraryError("依赖目录已存在但没有 Python，未覆盖；请更换 --home。")
    requirements = own_root / "requirements-corpus.txt"
    subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-cache-dir", "-r", str(requirements)], check=True)
    index = home / "poetry.sqlite3"
    if index.exists() and not args.rebuild:
        db = connect_readonly(index)
        try:
            metadata = read_metadata(db)
            if metadata["revision"] != CORPUS_REVISION or Path(metadata["source_root"]).resolve() != source.resolve():
                raise LibraryError("已有索引的来源或版本不同，未覆盖；请检查后使用 --rebuild 或更换 --home。")
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise LibraryError("已有索引完整性检查失败，请显式 --rebuild。")
            if not metadata["total_records"] or db.execute("SELECT count(*) FROM works").fetchone()[0] != metadata["total_records"]:
                raise LibraryError("索引记录数量与元数据不一致，请显式 --rebuild。")
            print(f"复用完整索引：{metadata['total_records']} 条；{index}")
            return 0
        finally:
            db.close()
    subprocess.run([str(python), str(own_root / "scripts/poetry_library.py"), "--home", str(home), "--json", "index"], check=True)
    print("语料原文、LICENSE、来源版本与本地检索索引已准备完成。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (LibraryError, OSError, subprocess.CalledProcessError) as exc:
        print(f"诗词库安装未完成：{exc}", file=sys.stderr)
        sys.exit(1)
