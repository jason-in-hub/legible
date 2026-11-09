"""Cross-family judge (OpenAI-compatible chat API) reusing judge_v2's prompts, both A/B orders, same win rule.
Needs an API credential for the host in the environment's network secrets (the proxy injects the header; the key below is a dummy).
usage: python3 judge_xfam.py MODEL_ID [--list]     --list prints available model ids and exits
Writes judge_xfam.jsonl (variant vs placebo, slim/full) and records the model id in each row."""
import json, pathlib, re, sys, time, urllib.request, concurrent.futures as cf
import judge_v2 as J
HOST = "https://api.openai.com/v1"
HDR = {"Content-Type": "application/json", "Authorization": "Bearer dummy-injected-by-proxy"}
def http(path, body=None):
    req = urllib.request.Request(HOST + path, data=json.dumps(body).encode() if body else None, headers=HDR)
    with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read())
def call(model, msg):
    err = ""
    for k in range(5):
        try:
            r = http("/chat/completions", {"model": model, "messages": [{"role": "system", "content": J.SYS}, {"role": "user", "content": msg}]})
            return json.loads(re.search(r"\{.*\}", r["choices"][0]["message"]["content"], re.S).group(0))
        except Exception as e: err = str(e); time.sleep(4 * 2 ** k)
    return {"error": err}
if __name__ == "__main__":
    if "--list" in sys.argv: print(sorted(m["id"] for m in http("/models")["data"])); sys.exit()
    model = sys.argv[1]; J.call = call
    d = J.load(); ids = sorted({k[0] for k in d}); out = J.ROOT / "judge_xfam.jsonl"
    comps = [("slim", "placebo"), ("full", "placebo")]
    done = {(j["id"], j["x"], j["y"]) for j in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    jobs = [(model, d, pid, x, y) for pid in ids for x, y in comps if (pid, x, y) not in done]
    with cf.ThreadPoolExecutor(4) as ex, open(out, "a") as fh:
        for r in ex.map(lambda a: J.one(*a), jobs):
            fh.write(json.dumps(r, ensure_ascii=False) + "\n"); fh.flush()
            print(r["id"], r["x"], r["y"], r["xy"].get("clarity", "ERR"), r["yx"].get("clarity", "ERR"), flush=True)
