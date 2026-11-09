"""Build controlled stimuli for the human self-paced-reading pilot.

For 12 of the v2 dense passages (original = condition `orig`), generate a rewrite under each of two system prompts
(`placebo`: one clarity sentence; `skill`: full legible SKILL.md + examples.md), with the SAME format constraint in the
user message (one plain paragraph, 110-150 words, no lists/headings/bold/line breaks), so reading-time differences
cannot come from formatting. Then generate 2 two-alternative comprehension questions per passage from the ORIGINAL
facts, and keep a question only if Opus judges it answerable, and answered the same way, in all three versions.

Output: stimuli.json  (list of {id, orig, placebo, skill, questions:[{q, correct, wrong}]})
Run: python3 build_stimuli.py   (resumable: caches each call in cache/)
"""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import re
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent
V2 = ROOT.parent / "v2"
SKILL = ROOT.parent.parent / "skills" / "legible"
BASE = "You are a helpful assistant."
PLACEBO = BASE + "\n\nWrite so a human reader understands every sentence on the first read. Prefer plain, clear sentences."
FULL = (BASE + "\n\nApply the following writing skill (its `write` operation) to everything you write in this conversation. Do not mention the skill.\n\n<skill>\n"
        + (SKILL / "SKILL.md").read_text() + "\n\n" + (SKILL / "references" / "examples.md").read_text() + "\n</skill>")
FORMAT = ("Rewrite the following so it is easier to read. Keep every fact and number. Output exactly one plain paragraph of 110 to 150 words: "
          "no headings, lists, bold, quotation marks around the whole text, or line breaks. Output only the paragraph.\n\n")
N = 12
(ROOT / "cache").mkdir(exist_ok=True)


def claude(model, system, prompt):
    key = hashlib.sha256((model + system + prompt).encode()).hexdigest()[:20]
    f = ROOT / "cache" / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())["r"]
    cmd = ["claude", "-p", prompt, "--model", model, "--system-prompt", system, "--tools", "", "--disable-slash-commands",
           "--setting-sources", "", "--no-session-persistence", "--output-format", "json"]
    err = ""
    for k in range(5):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=400, cwd="/tmp")
        try:
            res = json.loads(r.stdout)["result"].strip()
            if not res:
                raise ValueError("empty")
            f.write_text(json.dumps({"r": res}))
            return res
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(4 * 2 ** k)
    raise RuntimeError(err)


def flat(t):
    return re.sub(r"\s+", " ", t.replace("**", "")).strip()


def jparse(t):
    return json.loads(re.search(r"[\[{].*[\]}]", t, re.S).group(0))


def build(row):
    pid, orig = row["id"], flat(row["passage"])
    placebo = flat(claude("claude-sonnet-5-5", PLACEBO, FORMAT + orig))
    skill = flat(claude("claude-sonnet-5-5", FULL, FORMAT + orig))
    qs = jparse(claude("claude-opus-5-5", "You write reading-comprehension items. Output only JSON.",
        "Write 3 two-alternative comprehension questions about concrete facts stated in this passage (numbers, causes, who did what). "
        "Each must be answerable only from the passage, with one correct answer and one plausible wrong answer, each at most 8 words. "
        'Output JSON: [{"q": "...", "correct": "...", "wrong": "..."}, ...]\n\nPassage:\n' + orig))
    keep = []
    for q in qs:
        ok = True
        for name, txt in (("orig", orig), ("placebo", placebo), ("skill", skill)):
            v = jparse(claude("claude-opus-5-5", "You verify reading-comprehension items. Output only JSON.",
                f'Passage:\n{txt}\n\nQuestion: {q["q"]}\nOption 1: {q["correct"]}\nOption 2: {q["wrong"]}\n\n'
                'Can a reader pick the right option from this passage alone, and is it Option 1? Output JSON: {"answerable": true|false, "answer": 1|2}'))
            if not (v.get("answerable") is True and v.get("answer") == 1):
                ok = False
        if ok:
            keep.append(q)
    return {"id": pid, "orig": orig, "placebo": placebo, "skill": skill, "questions": keep[:2],
            "words": {"orig": len(orig.split()), "placebo": len(placebo.split()), "skill": len(skill.split())}}


if __name__ == "__main__":
    rows = [json.loads(l) for l in (V2 / "prompts_revise.jsonl").read_text().splitlines()][:N]
    with cf.ThreadPoolExecutor(3) as ex:
        out = list(ex.map(build, rows))
    good = [o for o in out if o["questions"]]
    print(f"{len(good)}/{len(out)} passages kept with >=1 verified question")
    for o in out:
        print(o["id"], o["words"], len(o["questions"]))
    (ROOT / "stimuli.json").write_text(json.dumps(good, ensure_ascii=False, indent=1))
