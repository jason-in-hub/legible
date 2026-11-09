"""v2 generation: arms base/placebo/full/slim x (30 write + 20 revise) prompts, writer claude-sonnet-5-5, isolated claude -p."""
import json, pathlib, subprocess, concurrent.futures as cf, sys
ROOT = pathlib.Path(__file__).resolve().parent
SK = ROOT.parent.parent / "skills" / "legible"
BASE = "You are a helpful assistant."
PLACEBO = BASE + "\n\nWrite so a human reader understands every sentence on the first read. Prefer plain, clear sentences."
FULL = (BASE + "\n\nApply the following writing skill (its `write` operation) to everything you write in this conversation. Do not mention the skill.\n\n<skill>\n"
        + (SK/"SKILL.md").read_text() + "\n\n" + (SK/"references"/"examples.md").read_text() + "\n</skill>")
SLIM = (BASE + "\n\nApply the following writing skill to everything you write in this conversation. Do not mention the skill.\n\n<skill>\n"
        + (SK/"SKILL.slim.md").read_text() + "\n</skill>")
ARMS = {"base": BASE, "placebo": PLACEBO, "full": FULL, "slim": SLIM}
MODEL = "claude-sonnet-5-5"
REV = "Rewrite the following so it is easier to read. Keep every fact and number.\n\n"
def tasks():
    for l in (ROOT/"prompts_write.jsonl").read_text().splitlines():
        p = json.loads(l); yield p["id"], p["setting"], p["prompt"]
    for l in (ROOT/"prompts_revise.jsonl").read_text().splitlines():
        p = json.loads(l); yield p["id"], "revise", REV + p["passage"]
def run(t, arm):
    pid, setting, prompt = t
    out = ROOT/"out"; out.mkdir(exist_ok=True)
    f = out/f"{pid}__{arm}.json"
    if f.exists(): return f"skip {f.name}"
    cmd = ["claude","-p",prompt,"--model",MODEL,"--system-prompt",ARMS[arm],"--tools","","--disable-slash-commands","--setting-sources","","--no-session-persistence","--output-format","json"]
    err = ""
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=400, cwd="/tmp")
        try:
            d = json.loads(r.stdout)
            if d.get("is_error") or not d.get("result"): raise ValueError(d.get("result") or r.stderr[:200])
            f.write_text(json.dumps({"id":pid,"setting":setting,"arm":arm,"model":MODEL,"prompt":prompt,"text":d["result"],"cost_usd":d.get("total_cost_usd")}, ensure_ascii=False, indent=1))
            return f"ok {f.name}"
        except Exception as e: err = str(e)
    return f"FAIL {f.name}: {err}"
if __name__ == "__main__":
    jobs = [(t, a) for t in tasks() for a in ARMS]
    with cf.ThreadPoolExecutor(8) as ex:
        for m in ex.map(lambda x: run(*x), jobs): print(m, flush=True)
