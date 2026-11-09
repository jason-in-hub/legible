# Pre-registration: legible A/B v2

Written and committed **before any v2 data was generated**. Check `git log` for the commit time against the first file in `eval/v2/out/`.

## Why v2
v1 (eval/README.md) found the full skill beat no instruction (32-6-2) but not a one-line placebo (7-18-15, n.s.), on n=20 prompts, single judge, one order per pair, and a detector lexicon edited after seeing data. v2 fixes those and tests two untested conditions.

## Arms (all with the same base system prompt "You are a helpful assistant.")
- `base`: nothing added.
- `placebo`: one sentence: "Write so a human reader understands every sentence on the first read. Prefer plain, clear sentences."
- `full`: SKILL.md + references/examples.md (v1's skill arm).
- `slim`: skills/legible/SKILL.slim.md (about 330 words, no bad examples).

## Tasks
- **write** (30 held-out prompts, none from v1): 10 chat, 10 code explanation, 10 essay. Writer: claude-sonnet-5-5, 1 sample per cell.
- **revise** (20 passages): dense, compressed AI-style passages (synthetic, generated once by claude-opus-5-5 with an instruction to write compressed expert prose using the constructions from the paper). Each arm gets: "Rewrite the following so it is easier to read. Keep every fact and number." Writer: claude-sonnet-5-5.

## Primary endpoints (fixed now)
For each task, the blind pairwise judge's clarity verdict on **slim vs placebo** and **full vs placebo**. A pair counts as a win only if the verdict agrees across both A/B orders; disagreement counts as a tie. Test: two-sided exact sign test on wins vs losses, ties excluded, alpha = 0.05, Holm-corrected over the 4 primary tests (2 comparisons x 2 tasks).
- Primary judge: claude-opus-5-5. Secondary judge: claude-haiku-5-5, reported but not used for the decision.

## Secondary endpoints
- vs base (same procedure).
- Length: words per response; the judge's completeness verdict; for revise, the judge's count of facts dropped (0 expected).
- Length-controlled comparison: pairs where the two responses are within 15% of each other in word count, reported separately.
- Features (stacked nouns, long subject-verb gaps, reduced relatives, complement-that omission) from score.py **exactly as it stood at commit of this file**. No detector edits after data. The inanimate-subject detector is reported as exploratory.

## Decision rule
- A variant "earns its tokens" if it beats placebo on the primary endpoint in at least one task (Holm-adjusted p < 0.05) and is not rated less complete than placebo in more pairs than more complete.
- If neither slim nor full earns it, legible is repositioned as an explainer and teaching material, not a prompt, and the README says so.

## Known limits (stated in advance)
- All judges are Claude models. No cross-family judge is available in this environment, and no human rater. Cross-family and human checks are listed as follow-up.
- Writer is a single model. Single-turn only.
- The revise inputs are synthetic.
