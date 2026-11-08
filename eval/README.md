# legible A/B eval

**Verdict:** the skill makes answers clearly easier to read than having no instruction at all. It doesn't beat a single sentence asking for clear writing (the placebo). If anything, it trends slightly worse. In single-turn use, as written, it isn't worth its ~7k tokens over that sentence.

## Design

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

## Results

### Blind judge (sample 1, 40 pairs per comparison, 0 parse errors)

| comparison | skill clearer | tie | other clearer | sign test | rereads per response (skill vs other) | more complete (skill / same / other) |
|---|---|---|---|---|---|---|
| skill vs base | **32** | 6 | 2 | p ≈ 7e-8 | 0.35 vs 1.15 | 3 / 9 / **28** |
| skill vs placebo | 7 | 18 | **15** | p = 0.13 (n.s.) | 0.70 vs 0.48 | 13 / 14 / 13 |

Breaking the placebo comparison down by setting:

- **Chat:** 4–10–6 (skill wins, ties, losses)
- **Code:** 2–3–5
- **Essay:** 1–5–4

### Features (Sonnet 5.5, 20 prompts; `*` marks a 95% bootstrap CI over prompts that excludes 0)

| metric | base | placebo | skill | skill − base | skill − placebo |
|---|---|---|---|---|---|
| words per response | 417 | 358 | 362 | −56 * | +3 |
| stacked nouns per 1k words | 5.58 | 2.32 | 3.08 | −2.50 * | +0.76 |
| subject–verb gap > 7 words, per 100 sentences | 3.47 | 2.31 | 2.61 | −0.86 | +0.30 |
| inanimate subject + animate verb, per 1k words | 0.92 | 0.75 | 1.06 | +0.14 | +0.31 |
| complement clauses missing *that* (share) | 0.84 | 0.96 | 0.81 | −0.04 | −0.10 |

Opus 5.5 shows the same pattern. Against base, the skill also lowers inanimate subjects (−0.73 *). Against the placebo, it shows *more* reduced object relatives (+1.48 *). Full tables are in `results/summary.md`, and every hit is listed in `results/hits.txt`.

## What it means

- **Confirmed:** any clarity instruction helps a lot over none. The skill's win over base is real (32–2).
- **Confirmed:** part of that win comes from saying less. The judge rated base as more complete in 28 of 40 pairs, and the skill responses are about 15% shorter. So "clearer" is partly "shorter".
- **Confirmed:** the skill adds nothing measurable over one sentence of instruction in single-turn chat, code or essays (7–15–18, not significant, trending the wrong way).
- **Inference:** two possible reasons. First, the one-line instruction may already capture the skill's main effect. Second, 70+ quoted bad sentences in `examples.md` may prime the very forms the skill is meant to suppress. Running a no-examples variant would separate the two.

## Limits

- n = 20 prompts. Single-turn only, while the paper's largest effects were in long multi-turn chat and agentic coding.
- The judge comes from the same model family as the writers, and no human reader was involved.
- The feature detectors are approximations (see Instrument 1 above).

## What would flip the verdict

The skill would earn its tokens if any of these beats the placebo:

1. A **slim skill**: the 7-row table only, without the examples.
2. **revise mode**: rewriting existing dense AI text, where a concrete checklist should beat "write clearly".
3. A **long multi-turn or agentic session**, where compression pressure builds up.

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

The full run cost about $3 in API usage.
