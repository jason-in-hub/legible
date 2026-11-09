"""v2 blind pairwise judge. Each pair is judged in BOTH A/B orders; a win needs both orders to agree, else tie (pre-registered).
Primary judge claude-opus-5-5 (4 comparisons); secondary claude-haiku-5-5 (2 primary comparisons).
usage: python3 judge_v2.py opus|haiku"""
import json, pathlib, re, subprocess, sys, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent
JUDGES = {"opus": ("claude-opus-5-5", [("slim","placebo"),("full","placebo"),("slim","base"),("full","base")]),
          "haiku": ("claude-haiku-5-5", [("slim","placebo"),("full","placebo")])}
SYS = "You are a careful reading-comprehension rater. You output only JSON."
HEAD = """A user sent this message:

<user_message>
{prompt}
</user_message>
{src}
Two assistant responses follow.

<response_A>
{a}
</response_A>

<response_B>
{b}
</response_B>

Rate them as a typical, attentive adult reader seeing each for the first time.
1. clarity: Which response can the reader understand faster on the first read, with fewer places where they must stop, reparse or reread? Judge sentence-level readability only, not style preference, tone, formatting or length as such.
2. completeness: Which response gives the user more of the information they need? "A", "B" or "same".
"""
REVISE_EXTRA = """3. dropped_A / dropped_B: how many facts or numbers from the original passage are missing or wrong in each rewrite (integers).
"""
TAIL = 'Output exactly this JSON and nothing else:\n{{"clarity": "A" | "B" | "tie", "completeness": "A" | "B" | "same"{extra}, "why": "<one sentence>"}}'
def load():
    d = {}
    for f in (ROOT/"out").glob("*.json"):
        r = json.loads(f.read_text()); d[(r["id"], r["arm"])] = r
    return d
def call(model, msg):
    cmd = ["claude","-p",msg,"--model",model,"--system-prompt",SYS,"--tools","","--disable-slash-commands","--setting-sources","","--no-session-persistence","--output-format","json"]
    err = ""
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=400, cwd="/tmp")
        try: return json.loads(re.search(r"\{.*\}", json.loads(r.stdout)["result"], re.S).group(0))
        except Exception as e: err = str(e)
    return {"error": err}
def one(model, d, pid, x, y):
    rx, ry = d[(pid, x)], d[(pid, y)]
    rev = rx["setting"] == "revise"
    src = ""
    if rev: src = "\nThe user asked for a rewrite of a passage; the original passage is in the message above.\n"
    res = {}
    for order in ("xy", "yx"):
        a, b = (rx, ry) if order == "xy" else (ry, rx)
        msg = HEAD.format(prompt=rx["prompt"], src=src, a=a["text"], b=b["text"]) + (REVISE_EXTRA if rev else "") + TAIL.format(extra=', "dropped_A": int, "dropped_B": int' if rev else "")
        j = call(model, msg)
        if "error" in j: res[order] = j; continue
        flip = order == "yx"
        mp = lambda v: {"A": "x", "B": "y", "tie": "tie", "same": "same"}[v] if not flip else {"A": "y", "B": "x", "tie": "tie", "same": "same"}[v]
        o = {"clarity": mp(j["clarity"]), "completeness": mp(j["completeness"]), "why": j.get("why", "")}
        if rev:
            o["dropped_x"] = j["dropped_B"] if flip else j["dropped_A"]; o["dropped_y"] = j["dropped_A"] if flip else j["dropped_B"]
        res[order] = o
    return {"id": pid, "setting": rx["setting"], "x": x, "y": y, "judge": model, "xy": res["xy"], "yx": res["yx"]}
if __name__ == "__main__":
    which = sys.argv[1]; model, comps = JUDGES[which]
    d = load(); ids = sorted({k[0] for k in d})
    out = ROOT/f"judge_{which}.jsonl"
    done = {(j["id"], j["x"], j["y"]) for j in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    jobs = [(model, d, pid, x, y) for pid in ids for x, y in comps if (pid,x) in d and (pid,y) in d and (pid,x,y) not in done]
    with cf.ThreadPoolExecutor(8) as ex, open(out, "a") as fh:
        for r in ex.map(lambda a: one(*a), jobs):
            fh.write(json.dumps(r, ensure_ascii=False) + "\n"); fh.flush()
            print(r["id"], r["x"], r["y"], r["xy"].get("clarity", "ERR"), r["yx"].get("clarity", "ERR"), flush=True)
