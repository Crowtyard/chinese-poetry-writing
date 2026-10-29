"""Full cold installation + system-Python fallback; run explicitly, not unittest.

Downloads the pinned corpus, builds the full index, repeats setup, runs all
tests without optional skips, and queries from an interpreter without OpenCC.
Use --home to retain the evidence directory. Windows/Linux CI use this same file.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from poetry_library import CORPUS_REVISION, venv_python


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    home = (args.home or Path(tempfile.mkdtemp(prefix="poetry-cold-install-")) / "corpus").resolve()
    if home.exists():
        raise RuntimeError("Cold-install target must not already exist; refusing reuse")
    env = dict(os.environ, PYTHONUTF8="1")

    def run(*argv):
        print(json.dumps({"cwd": str(root), "argv": list(map(str, argv))}, ensure_ascii=False), flush=True)
        return subprocess.run(list(map(str, argv)), cwd=root, env=env, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")

    for _ in range(2):
        result = run(sys.executable, "scripts/setup_poetry_library.py", "--home", home)
        print(result.stdout, flush=True)
    tests = run(venv_python(home / "venv"), "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    print(tests.stdout, flush=True)
    if "skipped=" in tests.stdout:
        raise RuntimeError("Optional tests must actually execute")
    # This probe venv has no pip or OpenCC, so the CLI must exec the corpus venv.
    probe = home.parent / (home.name + "-no-opencc")
    if probe.exists():
        raise RuntimeError("Refusing to overwrite probe environment")
    venv.EnvBuilder(with_pip=False).create(probe)
    ids = []
    for title in ("静夜思", "靜夜思"):
        result = run(venv_python(probe), root / "scripts/poetry_library.py", "--home", home,
                     "--json", "search", "--collection", "tang", "--author", "李白", "--title", title, "--count")
        data = json.loads(result.stdout)
        assert data["status"] == "OK" and data["total_matches"] == 1, data
        assert data["revision"] == CORPUS_REVISION, data
        ids.append(data["results"][0]["id"])
        print(result.stdout, flush=True)
    assert ids[0] == ids[1], ids
    print(f"COLD_INSTALL_PASS platform={os.name}; home={home}", flush=True)


if __name__ == "__main__":
    main()
