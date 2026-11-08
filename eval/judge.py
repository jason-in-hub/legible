"""Blind pairwise judge: which response does a reader understand faster on the first read?

For each model and prompt (sample 1), it compares skill vs base and skill vs placebo. A/B order is randomised (seeded)
and the judge never sees arm names or the skill text. It also reports which response is more complete, so a win by
cutting content shows up.

Usage: python3 judge.py --judge claude-opus-5-5 [--jobs 6]  -> results/judge.jsonl, results/judge.md
"""
import argparse
import concurrent.futures as cf
import json
import pathlib
import random
import re
import subprocess
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
SYS = "You are a careful reading-comprehension rater. You output only JSON."
TEMPLATE = """A user sent this message:

<user_message>
{prompt}
</user_message>

Two assistant responses follow.

<response_A>
{a}
</response_A>

<response_B>
{b}
</response_B>

Rate them as a typical, attentive adult reader seeing each for the first time.

1. clarity: Which response can the reader understand faster on the first read, with fewer places where they have to stop, reparse or reread a sentence? Judge sentence-level readability only, not style preference, tone, formatting or length as such.
2. reread_A / reread_B: How many sentences in each response would make a typical reader stop and reread? Give integers.
3. completeness: Which response gives the user more of the information they actually need? "A", "B" or "same".

Output exactly this JSON and nothing else:
{{"clarity": "A" | "B" | "tie", "reread_A": int, "reread_B": int, "completeness": "A" | "B" | "same", "why": "<one sentence>"}}"""


def load(model):
    d = {}
    for f in (ROOT / "out" / model).glob("*__s1.json"):
        r = json.loads(f.read_text())
        d[(r["id"], r["arm"])] = r
    return d


def judge_one(judge, prompt, x, y, key, rng_seed):
    rng = random.Random(rng_seed)
    flip = rng.random() < 0.5
    a, b = (y, x) if flip else (x, y)  # x is always the skill arm
    msg = TEMPLATE.format(prompt=prompt, a=a["text"], b=b["text"])
    cmd = ["claude", "-p", msg, "--model", judge, "--system-prompt", SYS, "--tools", "", "--disable-slash-commands",
           "--setting-sources", "", "--no-session-persistence", "--output-format", "json"]
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=400, cwd="/tmp")
        try:
            txt = json.loads(r.stdout)["result"]
            j = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
            unflip = {"A": "B", "B": "A"}
            m = (lambda v: unflip.get(v, v)) if flip else (lambda v: v)
            return {**key, "flip": flip, "clarity": {"A": "skill", "B": "other", "tie": "tie"}[m(j["clarity"])],
                    "reread_skill": j["reread_B"] if flip else j["reread_A"],
                    "reread_other": j["reread_A"] if flip else j["reread_B"],
                    "completeness": {"A": "skill", "B": "other", "same": "same"}[m(j["completeness"])], "why": j.get("why", "")}
        except Exception as e:  # noqa: BLE001
            err = str(e)
    return {**key, "error": err}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="claude-opus-5-5")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    prompts = {json.loads(l)["id"]: json.loads(l)["prompt"] for l in (ROOT / "prompts.jsonl").read_text().splitlines() if l.strip()}
    out = ROOT / "results" / "judge.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = {(j["model"], j["id"], j["vs"]) for j in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    tasks = []
    for mdir in sorted((ROOT / "out").iterdir()):
        d = load(mdir.name)
        for pid in sorted(prompts):
            for vs in ["base", "placebo"]:
                if (pid, "skill") in d and (pid, vs) in d and (mdir.name, pid, vs) not in done:
                    key = {"model": mdir.name, "id": pid, "setting": d[(pid, "skill")]["setting"], "vs": vs}
                    tasks.append((prompts[pid], d[(pid, "skill")], d[(pid, vs)], key, hash((mdir.name, pid, vs)) & 0xFFFF))
    with cf.ThreadPoolExecutor(a.jobs) as ex, open(out, "a") as fh:
        for res in ex.map(lambda t: judge_one(a.judge, *t), tasks):
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            fh.flush()
            print(res.get("model"), res.get("id"), res.get("vs"), res.get("clarity", res.get("error")), flush=True)
    summarise(out, a.judge)


def summarise(path, judge):
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if "error" not in r]
    lines = [f"# Blind pairwise judge (judge: {judge}; sample 1 per prompt; order randomised)\n",
             "| model | skill vs | n | skill clearer | tie | other clearer | rereads/response skill | other | more complete: skill | same | other |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for model in sorted({r["model"] for r in rows}):
        for vs in ["base", "placebo"]:
            rs = [r for r in rows if r["model"] == model and r["vs"] == vs]
            if not rs:
                continue
            c = Counter(r["clarity"] for r in rs)
            k = Counter(r["completeness"] for r in rs)
            rs_s = sum(r["reread_skill"] for r in rs) / len(rs)
            rs_o = sum(r["reread_other"] for r in rs) / len(rs)
            lines.append(f"| {model} | {vs} | {len(rs)} | {c['skill']} | {c['tie']} | {c['other']} | {rs_s:.2f} | {rs_o:.2f} | {k['skill']} | {k['same']} | {k['other']} |")
    (ROOT / "results" / "judge.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
