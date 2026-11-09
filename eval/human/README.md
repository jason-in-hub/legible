# Human reader pilot (ready to launch, not yet run)

Question it answers: **do readers read a legible-skill rewrite faster, or understand it better, than a one-line-placebo rewrite or the original dense text?** The automated judges in `../v2` are all Claude models, so this is the check that matters most.

Status: the experiment code and stimuli are built and tested end to end in a headless browser with synthetic readers. **No human has run it. There are no human results in this repo.**

## What participants do
Moving-window self-paced reading. A paragraph appears as dashes; each space-bar press reveals the next word and re-masks the previous one. After each paragraph they answer two verified two-choice comprehension questions. Each person reads 12 paragraphs, 4 per condition (`orig`, `placebo`, `skill`), assigned by Latin square so every paragraph appears in every condition across participants.

## Stimuli (`stimuli.json`)
- 12 dense synthetic passages from `../v2/prompts_revise.jsonl` (originals, 129–151 words).
- Placebo and skill rewrites generated with the same format constraint (one plain paragraph, no lists), so formatting can't cause timing differences. Rewrite lengths are 138–176 words, so the analysis uses per-word reading time with a word-length correction.
- 2 comprehension questions per passage, each checked by Opus as answerable from, and answered the same way by, all three versions.
- Caveat: stimuli are Claude-written and Claude-verified. A human proofread of all 36 texts and 24 questions should come before launch.

## Run it
1. Host `index.html` anywhere static (GitHub Pages, Netlify), or on Pavlovia.
2. Edit `CONFIG` at the top of the script in `spr_template.html`, then run `python3 make_html.py`:
   - `consentText`: your ethics-approved text. The placeholder is not valid consent.
   - `submitUrl`: an endpoint that accepts a JSON POST. If empty, participants download their file, which loses data on Prolific. Set it.
   - `completionUrl`: the Prolific completion link.
3. On Prolific, point the study URL at `https://YOUR-HOST/index.html?PROLIFIC_PID={{%PROLIFIC_PID%}}`. Restrict to desktop, fluent English, and not-done-before.
4. Collect the JSON files as `spr_*.json` in one folder, then `python3 analyze_human.py DATA_DIR`.

## Analysis rules (fixed before data)
Written in the header of `analyze_human.py`: exclusion thresholds, trimming, length residualisation, paired bootstrap across participants, accuracy reported beside speed. Confirmatory model for the full sample: `logRT ~ condition + length + (1|participant) + (1|item)`.

## Sample size
I can't give a trustworthy number. It depends on the real between-participant and between-item variance, which I don't have. Run **20 participants first**, read the CI width, then size the main run from it. Cost is `N × minutes/60 × hourly pay × (1 + platform fee)`; check Prolific's current minimum pay and fee (需驗證). A 12-paragraph session should take about 12–15 minutes (estimate).

## What this can't tell you
Self-paced reading measures time to read each word, not rereads, so it can miss the "stop and go back" cost the paper describes. Comprehension accuracy is the partner measure. An eye-tracking study would answer the rereading question directly.

## Tested, with what
`test_flow.js` drives the page with synthetic readers: 3 simulated participants, 12 trials each, 4/4/4 conditions, no JS errors. The analysis script then recovered effects planted in synthetic data (true skill−placebo −10 ms/word, estimated −8.5 [−9.7, −7.3]). That validates the code, not the skill.
