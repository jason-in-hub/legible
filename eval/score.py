"""Score generated responses on the paper's difficulty-linked features (approximations, see README).

Run with a Python that has spaCy + en_core_web_sm:  python score.py  -> results/features.csv, results/summary.md

Features (rates pooled per prompt x arm: total count / total words or sentences across samples)
  words, mean_sent_len          length controls: the skill must not win by padding or by cutting
  dep_len_std                   mean dependency length, standardised over sentence-length bins (paper App. B.3,
                                bin weights from the pooled corpus here instead of Wikipedia)
  long_subj_gap_per100s         subject->verb arcs spanning > 7 words, per 100 sentences   (check 2)
  stacked_nouns_per1k           noun compounds of 3+ nouns, per 1k words                   (check 4)
  reduced_orc_per1k             object relatives without a relativizer, per 1k words      (check 3)
  orc_that_per1k                object relatives with a relativizer, per 1k words
  comp_that_omit_share          complement clauses after know/think/say... without "that"  (check 3)
  inanim_animverb_per1k         inanimate subject + animate-only verb, per 1k words        (check 1, lexicon heuristic)
Not scored: denominal verbs and unattested bigrams (the paper used a trained classifier and reference corpora).
"""
import csv
import json
import pathlib
import random
import re
from collections import defaultdict

import spacy

ROOT = pathlib.Path(__file__).resolve().parent
NLP = spacy.load("en_core_web_sm")
BINS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 30)]
RELPRON = {"that", "which", "who", "whom", "whose"}
COMP_VERBS = {"know", "think", "say", "believe", "realize", "notice", "find", "feel", "mean", "hope", "suppose", "guess",
              "assume", "show", "learn", "remember", "forget", "see", "understand", "decide", "agree", "admit", "argue",
              "claim", "worry", "suggest", "tell", "promise", "bet", "doubt", "figure", "wish", "expect"}
ANIMATE_VERBS = {"expect", "want", "ask", "promise", "swallow", "bite", "eat", "believe", "decide", "hope", "love",
                 "hate", "refuse", "insist", "forget", "remember", "misunderstand", "understand", "ignore", "care",
                 "worry", "demand", "crave", "beg", "fear", "whisper", "scream", "fight", "hunt", "chase", "forgive",
                 "punish", "trust", "wonder", "pretend", "wish", "enjoy", "complain", "earn", "know", "think",
                 "lie", "hide", "judge", "notice", "realize", "grieve", "mourn", "celebrate", "sneak", "starve", "breathe",
                 "sleep", "die", "argue", "agree", "plead", "dare"}
ANIMATE_NOUNS = {"person", "people", "user", "student", "teacher", "parent", "partner", "friend", "kid", "child",
                 "dog", "cat", "puppy", "worker", "employee", "manager", "team", "family", "owner", "keeper", "stranger",
                 "reader", "writer", "developer", "client", "customer", "principal", "adult", "beginner", "renter",
                 "buyer", "landlord", "player", "guitarist", "musician", "human", "man", "woman", "guy", "boss",
                 "colleague", "coworker", "neighbor", "roommate", "everyone", "someone", "anyone", "nobody", "somebody",
                 "everybody", "one", "viewer", "audience", "director", "filmmaker", "animal", "pet", "trainer", "vet",
                 "breed", "officer", "police", "finder", "candidate", "recruiter", "mentor", "coach", "staff", "volunteer",
                 "adviser", "advisor", "expert", "doctor", "company", "school", "government", "administrator", "peer",
                 "classmate", "other", "critic", "supporter", "opponent", "girl", "boy", "counselor", "graduate", "senior", "relative", "salesperson", "outlier", "rescue", "shelter", "someone", "anyone", "everyone", "brain", "mind", "body", "eye", "ear", "heart"}
ANIMATE_PRON = {"i", "you", "he", "she", "we", "they", "who", "me", "him", "her", "us", "them", "yourself", "myself"}


def clean(text: str) -> list[str]:
    """Prose blocks only: drop code fences, swap inline code for a placeholder noun, strip markdown, split blocks."""
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", "it", text)
    blocks = []
    for line in text.split("\n"):
        line = re.sub(r"^\s*(#+|[-*+]|\d+[.)]|>)\s*", "", line)
        line = line.replace("**", "").replace("__", "").replace("|", " ").strip()
        if re.fullmatch(r"[-:\s]*", line):
            continue
        blocks.append(line)
    return blocks


def words_of(sent) -> list:
    return [t for t in sent if not t.is_punct and not t.is_space]


def is_inanimate(subj) -> bool:
    lw = subj.lower_
    if subj.pos_ == "PRON":
        return lw in {"it", "this", "that", "these", "those", "which", "what"}
    if subj.ent_type_ in {"PERSON", "NORP", "ORG", "GPE"}:
        return False
    return subj.pos_ in {"NOUN", "PROPN"} and subj.lemma_.lower() not in ANIMATE_NOUNS


def analyse(text: str) -> dict:
    c = defaultdict(float)
    c["bin_sum"] = {b: 0.0 for b in BINS}
    c["bin_n"] = {b: 0 for b in BINS}
    hits = []
    for block in clean(text):
        doc = NLP(block)
        for s in doc.sents:
            ws = words_of(s)
            if not ws:
                continue
            n = len(ws)
            c["words"] += n
            c["sents"] += 1
            idx = {t.i: k for k, t in enumerate(ws)}  # word position, punctuation skipped
            arcs = [abs(idx[t.i] - idx[t.head.i]) for t in ws if t.head.i != t.i and t.head.i in idx]
            for b in BINS:
                if b[0] <= n <= b[1] and arcs:
                    c["bin_sum"][b] += sum(arcs)
                    c["bin_n"][b] += len(arcs)
            for t in ws:
                # check 2: subject far from its verb
                if t.dep_ in {"nsubj", "nsubjpass"} and t.head.i in idx and abs(idx[t.head.i] - idx[t.i]) - 1 > 7:
                    c["long_gap"] += 1
                    hits.append(("gap", s.text))
                # check 4: 3+ stacked nouns, counted once at the head of the compound
                if t.pos_ in {"NOUN", "PROPN"} and t.dep_ != "compound":
                    chain = [x for x in t.subtree if x.dep_ == "compound" and x.pos_ in {"NOUN", "PROPN"}]
                    if len(chain) >= 2:
                        c["stack"] += 1
                        hits.append(("stack", " ".join(x.text for x in sorted(chain + [t], key=lambda y: y.i))))
                # check 3: object relatives, reduced or not
                if t.dep_ == "relcl":
                    subj = [x for x in t.children if x.dep_ in {"nsubj", "nsubjpass"}]
                    if subj and subj[0].lower_ not in RELPRON and not any(x.dep_ == "dobj" and x.lower_ not in RELPRON for x in t.children):
                        rel = any(x.lower_ in RELPRON and x.i < subj[0].i for x in t.subtree)
                        c["orc_that" if rel else "orc_red"] += 1
                        if not rel:
                            hits.append(("orc", s.text))
                # check 3: complement "that"
                if t.dep_ == "ccomp" and t.head.lemma_.lower() in COMP_VERBS and t.i > t.head.i and any(x.dep_ in {"nsubj", "nsubjpass"} for x in t.children):
                    if t.tag_ == "VB" or any(x.dep_ == "aux" and x.lower_ == "to" for x in t.children):
                        continue  # an infinitive ("expects you to remember"), not a finite complement clause
                    between = doc[t.head.i + 1: t.i]
                    if any(x.text in {'"', "“", ":"} for x in between):
                        continue  # quoted speech, not a complement clause
                    c["comp"] += 1
                    if not any(x.dep_ == "mark" and x.lower_ == "that" for x in t.children):
                        c["comp_omit"] += 1
                # check 1: inanimate subject, animate-only verb
                if t.dep_ == "nsubj" and t.head.pos_ == "VERB" and t.head.lemma_.lower() in ANIMATE_VERBS and is_inanimate(t):
                    c["inanim"] += 1
                    hits.append(("inanim", f"[{t.text} -> {t.head.text}] " + s.text))
    num = sum(c["bin_sum"][b] for b in BINS)
    return {"words": c["words"], "sents": c["sents"], "long_gap": c["long_gap"], "stack": c["stack"],
            "orc_red": c["orc_red"], "orc_that": c["orc_that"], "comp": c["comp"], "comp_omit": c["comp_omit"],
            "inanim": c["inanim"], "bin_sum": {f"{a}-{b}": c["bin_sum"][(a, b)] for a, b in BINS},
            "bin_n": {f"{a}-{b}": c["bin_n"][(a, b)] for a, b in BINS}, "_hits": hits, "_arcs": num}


def main() -> None:
    recs = []
    for f in sorted((ROOT / "out").glob("*/*.json")):
        r = json.loads(f.read_text())
        r["feat"] = analyse(r["text"])
        recs.append(r)
    (ROOT / "results").mkdir(exist_ok=True)

    # bin weights for dependency length: each bin's share of all arcs in the pooled corpus
    keys = [f"{a}-{b}" for a, b in BINS]
    tot = {k: sum(r["feat"]["bin_n"][k] for r in recs) for k in keys}
    wsum = sum(tot.values())
    W = {k: tot[k] / wsum for k in keys}

    # pool per (model, prompt, arm)
    cell = defaultdict(lambda: defaultdict(float))
    for r in recs:
        g = cell[(r["model"], r["id"], r["arm"])]
        g["setting"] = r["setting"]
        g["n"] += 1
        for k in ["words", "sents", "long_gap", "stack", "orc_red", "orc_that", "comp", "comp_omit", "inanim"]:
            g[k] += r["feat"][k]
        for k in keys:
            g["bs_" + k] += r["feat"]["bin_sum"][k]
            g["bn_" + k] += r["feat"]["bin_n"][k]

    def metrics(g):
        dl_num = sum(W[k] * (g["bs_" + k] / g["bn_" + k]) for k in keys if g["bn_" + k])
        dl_den = sum(W[k] for k in keys if g["bn_" + k])
        return {
            "words": g["words"] / g["n"],
            "mean_sent_len": g["words"] / max(g["sents"], 1),
            "dep_len_std": dl_num / dl_den if dl_den else float("nan"),
            "long_subj_gap_per100s": 100 * g["long_gap"] / max(g["sents"], 1),
            "stacked_nouns_per1k": 1000 * g["stack"] / max(g["words"], 1),
            "reduced_orc_per1k": 1000 * g["orc_red"] / max(g["words"], 1),
            "orc_that_per1k": 1000 * g["orc_that"] / max(g["words"], 1),
            "comp_that_omit_share": g["comp_omit"] / g["comp"] if g["comp"] else float("nan"),
            "inanim_animverb_per1k": 1000 * g["inanim"] / max(g["words"], 1),
        }

    rows = []
    for (model, pid, arm), g in sorted(cell.items()):
        rows.append({"model": model, "id": pid, "setting": g["setting"], "arm": arm, "samples": int(g["n"]), **metrics(g)})
    with open(ROOT / "results" / "features.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # paired differences across prompts, bootstrap 95% CI
    M = [k for k in rows[0] if k not in {"model", "id", "setting", "arm", "samples"}]
    by = {(r["model"], r["id"], r["arm"]): r for r in rows}
    rng = random.Random(0)
    out = ["# A/B results (auto-generated by score.py)\n",
           f"Responses scored: {len(recs)}. Dependency-length bin weights (pooled corpus): " + ", ".join(f"{k}: {W[k]:.2f}" for k in keys) + "\n"]
    for model in sorted({r["model"] for r in rows}):
        for scope in ["all", "chat", "code", "essay"]:
            ids = sorted({r["id"] for r in rows if r["model"] == model and (scope == "all" or r["setting"] == scope)})
            out.append(f"\n## {model} · {scope} (n = {len(ids)} prompts)\n")
            out.append("| metric | base | placebo | skill | skill − base [95% CI] | skill − placebo [95% CI] |")
            out.append("|---|---|---|---|---|---|")
            for m in M:
                def vals(arm):
                    return [by[(model, i, arm)][m] for i in ids if (model, i, arm) in by]
                means = {a: _mean([v for v in vals(a) if v == v]) for a in ["base", "placebo", "skill"]}
                cis = []
                for ref in ["base", "placebo"]:
                    d = [by[(model, i, "skill")][m] - by[(model, i, ref)][m] for i in ids
                         if (model, i, "skill") in by and (model, i, ref) in by
                         and by[(model, i, "skill")][m] == by[(model, i, "skill")][m] and by[(model, i, ref)][m] == by[(model, i, ref)][m]]
                    cis.append(_fmt_ci(d, rng))
                out.append(f"| {m} | {means['base']:.2f} | {means['placebo']:.2f} | {means['skill']:.2f} | {cis[0]} | {cis[1]} |")
    (ROOT / "results" / "summary.md").write_text("\n".join(out) + "\n")

    # a sample of what each detector caught, for a human sanity check
    with open(ROOT / "results" / "hits.txt", "w") as fh:
        for r in recs:
            for kind, s in r["feat"]["_hits"]:
                fh.write(f"{r['model']}\t{r['arm']}\t{r['id']}\t{kind}\t{s.strip()[:220]}\n")
    print((ROOT / "results" / "summary.md").read_text())


def _mean(v):
    return sum(v) / len(v) if v else float("nan")


def _fmt_ci(d, rng, B=10000):
    if len(d) < 3:
        return "n/a"
    boots = sorted(_mean([d[rng.randrange(len(d))] for _ in d]) for _ in range(B))
    lo, hi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
    star = " *" if lo > 0 or hi < 0 else ""
    return f"{_mean(d):+.2f} [{lo:+.2f}, {hi:+.2f}]{star}"


if __name__ == "__main__":
    main()
