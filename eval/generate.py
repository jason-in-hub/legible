"""Generate A/B/C responses with the `claude` CLI, isolated: our system prompt only, no tools, no skills, no settings.

Arms
  base     "You are a helpful assistant."
  placebo  base + one sentence asking for clear, first-read prose (does the skill beat a cheap instruction?)
  skill    base + skills/legible/SKILL.md + references/examples.md

Usage: python3 generate.py --model claude-sonnet-5-5 --samples 2 [--jobs 6]
Output: out/<model>/<prompt_id>__<arm>__s<k>.json (skips files that already exist, so reruns resume).
"""
import argparse
import concurrent.futures as cf
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
SKILL = ROOT.parent / "skills" / "legible"
BASE = "You are a helpful assistant."
PLACEBO = BASE + "\n\nWrite so a human reader understands every sentence on the first read. Prefer plain, clear sentences."
SKILL_PROMPT = (
    BASE
    + "\n\nApply the following writing skill (its `write` operation) to everything you write in this conversation. "
    + "Do not mention the skill.\n\n<skill>\n"
    + (SKILL / "SKILL.md").read_text()
    + "\n\n"
    + (SKILL / "references" / "examples.md").read_text()
    + "\n</skill>"
)
ARMS = {"base": BASE, "placebo": PLACEBO, "skill": SKILL_PROMPT}


def run(model: str, p: dict, arm: str, k: int, out: pathlib.Path) -> str:
    f = out / f"{p['id']}__{arm}__s{k}.json"
    if f.exists():
        return f"skip {f.name}"
    cmd = [
        "claude", "-p", p["prompt"], "--model", model, "--system-prompt", ARMS[arm],
        "--tools", "", "--disable-slash-commands", "--setting-sources", "",
        "--no-session-persistence", "--output-format", "json",
    ]
    for attempt in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=400, cwd="/tmp")
        try:
            d = json.loads(r.stdout)
            if d.get("is_error") or not d.get("result"):
                raise ValueError(d.get("result") or r.stderr[:300])
            rec = {"id": p["id"], "setting": p["setting"], "arm": arm, "sample": k, "model": model,
                   "text": d["result"], "cost_usd": d.get("total_cost_usd"), "usage": d.get("usage")}
            f.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
            return f"ok {f.name}"
        except Exception as e:  # noqa: BLE001
            err = str(e)
    return f"FAIL {f.name}: {err}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    prompts = [json.loads(l) for l in (ROOT / "prompts.jsonl").read_text().splitlines() if l.strip()]
    out = ROOT / "out" / a.model
    out.mkdir(parents=True, exist_ok=True)
    tasks = [(p, arm, k) for p in prompts for arm in ARMS for k in range(1, a.samples + 1)]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for msg in ex.map(lambda t: run(a.model, *t, out), tasks):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
