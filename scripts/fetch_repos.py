#!/usr/bin/env python3
"""从 GitHub API 核实 seed.json 里每个仓库的星数/语言/最近推送/存档状态。"""
import json, subprocess, sys, time
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent / "data" / "seed.json"
OUT  = SEED.parent / "repos.json"
PROXY = "http://127.0.0.1:7897"

def gh_api(path):
    # gh CLI 自带 token 和代理配置，比裸 curl 稳
    r = subprocess.run(["gh", "api", path, "--cache", "1h"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)

def main():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    repos = seed["repos"]
    out, bad = [], []
    for i, item in enumerate(repos):
        full = item["repo"]
        try:
            d = gh_api(f"/repos/{full}")
            row = {
                "repo": full, "cat": item["cat"], "zh": item["zh"],
                "stars": d.get("stargazers_count", 0),
                "lang": d.get("language") or "",
                "pushed": (d.get("pushed_at") or "")[:10],
                "archived": bool(d.get("archived")),
                "desc": (d.get("description") or "")[:140],
                "homepage": d.get("homepage") or "",
            }
            out.append(row)
            print(f"[{i+1}/{len(repos)}] {full}: {row['stars']}★ {row['pushed']}" + (" [ARCHIVED]" if row["archived"] else ""))
        except Exception as e:
            bad.append(full)
            print(f"[{i+1}/{len(repos)}] {full}: FAIL {e}")
        time.sleep(0.4)
    data = {"site": seed["site"], "categories": seed["categories"], "repos": out}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nOK {len(out)} repos -> {OUT}")
    if bad:
        print("FAILED:", *bad, sep="\n  ")
        sys.exit(1)

if __name__ == "__main__":
    main()
