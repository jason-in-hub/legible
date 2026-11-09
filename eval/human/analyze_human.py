"""Analyse spr_*.json files (one per participant) in a directory.  usage: python3 analyze_human.py DATA_DIR [--simulated]

Pre-specified rules (fixed before any real data):
  Participant exclusion: comprehension accuracy < 60% overall, or median word RT < 120 ms (button mashing).
  Word exclusion: first and last word of each passage; RT < 100 ms or > 3000 ms; sentence-final spillover is kept.
  Length correction: RT is residualised on word length (characters) with one pooled linear fit across all kept words.
Primary endpoint: mean residual RT per word, per participant x condition; paired bootstrap (10,000) across participants for
  skill - placebo and skill - orig, 95% CI.   Secondary: comprehension accuracy per condition (same test).
Notes: self-paced reading measures time to read, not rereads; a skill that merely shortens words or sentences can look faster,
  which is why accuracy is reported beside RT. Mixed-effects (lme4: logRT ~ cond + len + (1|participant) + (1|item)) is the
  recommended confirmatory model for the full sample; this script gives the robust paired summary.
"""
import glob, json, pathlib, random, statistics as st, sys
d = pathlib.Path(sys.argv[1]); sim = "--simulated" in sys.argv
P = [json.loads(open(f).read()) for f in sorted(glob.glob(str(d / "spr_*.json")))]
keep = []
for p in P:
    rts = [r for t in p["trials"] for r in t["rts"]]
    acc = [a["correct"] for t in p["trials"] for a in t["answers"]]
    if not rts or sum(acc) / len(acc) < .60 or st.median(rts) < 120: continue
    keep.append(p)
print(f"participants: {len(P)} read, {len(keep)} kept" + ("   *** SIMULATED DATA: code test only ***" if sim else ""))
rows = []
for p in keep:
    for t in p["trials"]:
        n = len(t["rts"])
        for i, (w, r) in enumerate(zip(t["words"], t["rts"])):
            if i == 0 or i >= n - 1 or r < 100 or r > 3000: continue
            rows.append((p["pid"], t["cond"], t["id"], len(w.strip(".,;:()\"'")), r))
mx = st.mean(r[3] for r in rows); my = st.mean(r[4] for r in rows)
b = sum((r[3] - mx) * (r[4] - my) for r in rows) / sum((r[3] - mx) ** 2 for r in rows); a = my - b * mx
print(f"length fit: RT = {a:.0f} + {b:.1f} ms/char   ({len(rows)} words)")
cell = {}
for pid, c, item, L, r in rows: cell.setdefault((pid, c), []).append(r - (a + b * L))
by = {c: {p["pid"]: st.mean(cell[(p["pid"], c)]) for p in keep if (p["pid"], c) in cell} for c in ("orig", "placebo", "skill")}
acc = {c: {} for c in by}
for p in keep:
    for c in by:
        v = [x["correct"] for t in p["trials"] if t["cond"] == c for x in t["answers"]]
        if v: acc[c][p["pid"]] = sum(v) / len(v)
rng = random.Random(0)
def boot(x, y, B=10000):
    ids = sorted(set(x) & set(y)); dif = [x[i] - y[i] for i in ids]
    m = st.mean(dif); bs = sorted(st.mean(rng.choices(dif, k=len(dif))) for _ in range(B))
    return len(ids), m, bs[int(.025 * B)], bs[int(.975 * B) - 1]
print("\nmean residual RT per word (ms; negative = faster than length-predicted):")
for c in by: print(f"  {c:8s} {st.mean(by[c].values()):+7.1f}   accuracy {st.mean(acc[c].values()):.2f}")
for lab, x, y in (("skill - placebo", "skill", "placebo"), ("skill - orig", "skill", "orig"), ("placebo - orig", "placebo", "orig")):
    n, m, lo, hi = boot(by[x], by[y]); n2, m2, lo2, hi2 = boot(acc[x], acc[y])
    print(f"  {lab:16s} RT {m:+6.1f} ms [{lo:+.1f}, {hi:+.1f}] (n={n})   accuracy {m2:+.3f} [{lo2:+.3f}, {hi2:+.3f}]")
