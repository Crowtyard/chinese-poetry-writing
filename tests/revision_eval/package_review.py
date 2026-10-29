"""Replay explicit pairs, keep real prosody logs, create a human review packet.

This does not call a model, assign aesthetic scores, or simulate human verdicts.
Cases include historical samples and constructed controls, not controlled A/B.
"""
import argparse
import json
from pathlib import Path
import random
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prosody", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=20261029)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    private = args.output / "private"
    private.mkdir()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    rng = random.Random(args.seed)
    rows, key = [], {}
    blind = ["# 匿名局部修订比较（非独立新旧版全流程 A/B）", "",
             "按题面判断事实保留、表达自然度、意象作用，各写句子证据。",
             "可选 A 更好 / B 更好 / 相同 / 都不合适；不必选出赢家。",
             "先盲读，再由组织者另发格律结果；不要据技术绿灯决定诗好坏。", ""]
    for case in cases:
        if case["before"] is None or case["after"] is None:
            continue
        choices = ["before", "after"]
        rng.shuffle(choices)
        key[case["id"]] = dict(zip(("A", "B"), choices))
        blind += ["## " + case["id"], "", case["input"], ""]
        for label, side in zip(("A", "B"), choices):
            poem = case[side]
            argv = [sys.executable, str(args.prosody.resolve() / "scripts/check_poem.py"),
                    "--poem", poem, "--form", case.get("form", "jueju7"), "--rhyme-profile", "xinyun18", "--json"]
            proc = subprocess.run(argv, cwd=args.prosody, capture_output=True, encoding="utf-8")
            (private / f"{case['id']}-{side}.json").write_text(proc.stdout, encoding="utf-8")
            report = json.loads(proc.stdout)
            if proc.returncode not in (0, 1, 2) or report.get("verdict") not in ("PASS", "WARN", "FAIL"):
                raise RuntimeError(f"Invalid check output: {argv}; stderr={proc.stderr}")
            rows.append({"id": case["id"], "side": side, "cwd": str(args.prosody.resolve()),
                         "argv": argv, "exit_code": proc.returncode, "verdict": report["verdict"],
                         "human_review": "PENDING", "provenance": case["provenance"], "risk": case["risk"]})
            blind += [f"**{label}**", "", poem, ""]
        blind += ["评阅：____；事实依据：____；自然度：____；意象作用：____。", ""]
    (private / "mapping.json").write_text(json.dumps(key, ensure_ascii=False, indent=2), encoding="utf-8")
    (private / "technical-results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output / "blind-review.md").write_text("\n".join(blind), encoding="utf-8")
    held = [c for c in cases if c["split"] == "heldout"]
    (args.output / "heldout-prompts.json").write_text(json.dumps(held, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{k: r[k] for k in ("id", "side", "exit_code", "verdict", "human_review")} for r in rows], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
