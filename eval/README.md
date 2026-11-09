# legible A/B eval

**Verdict after v2: legible does not beat a one-sentence instruction, and the full version is measurably worse than it.** Any clarity instruction helps a lot over none. The skill helps by the same amount as one sentence, and adds nothing on top. Following the rule I set before running v2, legible is now an explainer and teaching resource, not a prompt you should install to improve output.

The practical takeaway is the placebo sentence itself:

> Write so a human reader understands every sentence on the first read. Prefer plain, clear sentences.

## v2 (pre-registered, `eval/v2/`)

[`PREREGISTRATION.md`](v2/PREREGISTRATION.md) was committed before any v2 data existed. Full tables are in [`v2/results/v2.md`](v2/results/v2.md).

**What changed from v1:** 30 new held-out write prompts plus a new revise task (20 dense passages to rewrite), a slim skill variant (220 words, no bad examples), both A/B orders per pair (a win needs both to agree), a second judge, a frozen feature scorer, and a Holm correction over four primary tests.

| variant vs one-line placebo | task | wins | ties | losses | Holm p | placebo judged more complete |
|---|---|---|---|---|---|---|
| slim | write | 3 | 19 | 8 | 0.23 | 6 of 30 |
| slim | revise | 2 | 8 | 10 | 0.12 | 3 of 20 |
| **full** | **write** | **1** | **16** | **13** | **0.007** | 5 of 30 |
| full | revise | 1 | 11 | 8 | 0.12 | 3 of 20 |

- **Confirmed:** the pre-registered rule says neither variant earns its tokens. The only significant result is against the skill: full is worse than the placebo on write tasks.
- **Confirmed:** the revise hypothesis failed. I expected a concrete checklist to beat "write clearly" when fixing existing dense text. It lost 10–2 (slim) and 8–1 (full) on the primary judge, and Haiku, the second judge, agrees on revise (slim 0–11, full 0–8 against the placebo).
- **Confirmed:** length doesn't explain it. Among pairs within 15% of each other in word count, the skill still loses more than it wins (slim write 1–8, full write 0–7).
- **Confirmed, exploratory (not pre-registered):** the placebo beats no instruction 25–0 on write and 12–0 on revise, so "any clarity instruction works" holds.
- **Confirmed:** against no instruction, both skill variants win clearly (slim 23–0 write, full 21–1 write). That's v1's result again, and the placebo gets the same win.
- **Inference:** the skill's sentences got longer in revise (mean 14.3 words for full, 14.5 for slim, against 11.2 for the placebo), so a checklist may make the model repair constructions without splitting sentences. I didn't test that directly.

**Limits of v2:**
- Every judge is a Claude model, and no cross-family judge or human was available.
- Many pairs flip with the A/B order (19 of 30 for slim write), so most verdicts are ties and only agreed wins count. Position noise is large.
- Single writer model, single turn.
- The revise inputs are synthetic.
- Feature results were not a primary endpoint. The skill lowers stacked nouns about as much as the placebo does (write: 2.5 against 2.5), and no more.

**What would change this verdict:**
1. A cross-family judge, or better, human readers.
2. Long multi-turn or agentic sessions, where the paper found the largest effects. I tested none.
3. A different writer model. All writers here were Sonnet 5.5, a recent model that the paper found already writes better than its predecessors.

## v1 (exploratory, 20 prompts)

### Design

- **Models:** Claude Sonnet 5.5 (2 samples per cell) and Claude Opus 5.5 (1 sample per cell). Each generation call is an isolated `claude -p` with only our system prompt: no tools, no skills, no settings. That's 180 responses.
- **Arms:**
  - `base`: "You are a helpful assistant."
  - `placebo`: `base` plus one sentence, "Write so a human reader understands every sentence on the first read. Prefer plain, clear sentences."
  - `skill`: `base` plus the full `SKILL.md` and `examples.md`.
- **Prompts (20):**
  - the paper's 10 chat openers, verbatim (Table 5a)
  - 5 code explanations, written for this eval
  - 5 PERSUADE-style essays, with wording written for this eval
- **Instrument 1, features:** `score.py` approximates the paper's spaCy features with `en_core_web_sm`. The paper used `trf` plus an external classifier. Each detector was first checked against the paper's own example sentences, firing on the bad version and staying quiet on the good one. The inanimate-subject detector is a lexicon heuristic; a manual audit found roughly two thirds of its hits are real. Denominal verbs and rare bigrams aren't scored.
- **Instrument 2, judge:** `judge.py` runs a blind pairwise comparison with Opus 5.5 as the judge. A/B order is randomised and the judge never sees arm names or the skill. It rates which response is clearer on first read, counts the sentences that need a reread, and says which response is more complete.

### Results

#### Blind judge (sample 1, 40 pairs per comparison, 0 parse errors)

| comparison | skill clearer | tie | other clearer | sign test | rereads per response (skill vs other) | more complete (skill / same / other) |
|---|---|---|---|---|---|---|
| skill vs base | **32** | 6 | 2 | p ≈ 7e-8 | 0.35 vs 1.15 | 3 / 9 / **28** |
| skill vs placebo | 7 | 18 | **15** | p = 0.13 (n.s.) | 0.70 vs 0.48 | 13 / 14 / 13 |

Breaking the placebo comparison down by setting:

- **Chat:** 4–10–6 (skill wins, ties, losses)
- **Code:** 2–3–5
- **Essay:** 1–5–4

#### Features (Sonnet 5.5, 20 prompts; `*` marks a 95% bootstrap CI over prompts that excludes 0)

| metric | base | placebo | skill | skill − base | skill − placebo |
|---|---|---|---|---|---|
| words per response | 417 | 358 | 362 | −56 * | +3 |
| stacked nouns per 1k words | 5.58 | 2.32 | 3.08 | −2.50 * | +0.76 |
| subject–verb gap > 7 words, per 100 sentences | 3.47 | 2.31 | 2.61 | −0.86 | +0.30 |
| inanimate subject + animate verb, per 1k words | 0.92 | 0.75 | 1.06 | +0.14 | +0.31 |
| complement clauses missing *that* (share) | 0.84 | 0.96 | 0.81 | −0.04 | −0.10 |

Opus 5.5 shows the same pattern. Against base, the skill also lowers inanimate subjects (−0.73 *). Against the placebo, it shows *more* reduced object relatives (+1.48 *). Full tables are in `results/summary.md`, and every hit is listed in `results/hits.txt`.

## What v1 showed

- **Confirmed:** any clarity instruction helps a lot over none. The skill's win over base is real (32–2).
- **Confirmed:** part of that win comes from saying less. The judge rated base as more complete in 28 of 40 pairs, and the skill responses are about 15% shorter. So "clearer" is partly "shorter".
- **Confirmed:** the skill adds nothing measurable over one sentence of instruction in single-turn chat, code or essays (7–15–18, not significant, trending the wrong way).
- **Inference:** two possible reasons. First, the one-line instruction may already capture the skill's main effect. Second, 70+ quoted bad sentences in `examples.md` may prime the very forms the skill is meant to suppress. Running a no-examples variant would separate the two.

### Limits

- n = 20 prompts. Single-turn only, while the paper's largest effects were in long multi-turn chat and agentic coding.
- The judge comes from the same model family as the writers, and no human reader was involved.
- The feature detectors are approximations (see Instrument 1 above).

## What v1 left open

v1 suggested three follow-ups: a slim skill, revise mode, and long multi-turn sessions. v2 tested the first two and both failed. Only multi-turn remains untested.

## Reproduce

Generate the responses:

```bash
python3 generate.py --model claude-sonnet-5-5 --samples 2
```

```bash
python3 generate.py --model claude-opus-5-5 --samples 1
```

Score them (needs spaCy and `en_core_web_sm`):

```bash
python score.py
```

Run the judge:

```bash
python3 judge.py --judge claude-opus-5-5
```

v1 cost about $3 in API usage.

For v2, run these from `eval/v2/`. The judge scripts skip pairs that are already done, so you can rerun them after a failure:

```bash
python3 make_revise.py        # only to regenerate the revise inputs; prompts_revise.jsonl is committed
python3 generate_v2.py        # 200 responses, Sonnet 5.5 as writer
python3 judge_v2.py opus      # primary judge, 200 pairs x 2 orders
python3 judge_v2.py haiku     # secondary judge, 100 pairs x 2 orders
python3 judge_v2.py opusx     # exploratory placebo vs base
python analyze_v2.py          # needs spaCy; writes results/v2.md
```

The first judge run lost 112 Opus pairs to parse errors, caused by too many parallel calls. I deleted only those pairs, added a backoff and reran them at lower concurrency. No judged pair was dropped or edited by hand. v2 cost roughly $15 in API usage.
