---
name: legible
description: Write and revise text so a human reader understands it on the first pass. Targets the sentence-level constructions that frontier models overuse and that measurably slow human readers (Clark, Martin & Mahowald 2026, "Why is AI-generated language so hard to understand?", arXiv:2610.29162) - inanimate subjects doing animate things, long subject-verb gaps, dropped "that", stacked nouns, nouns forced into verbs, and coined word pairs. Use when writing explanations, chat answers, summaries, code-review or PR text, commit messages, docs, reports or essays for people to read; when asked to make text clearer, plainer, easier to read, or reader-friendly; or when a draft is dense, clipped, or "sounds like AI". Not a detector-evasion tool and does no model attribution.
license: MIT
metadata:
  version: "0.1.0"
  source: "arXiv:2610.29162v1"
---

# Legible — write for the reader's parser

The reader reads one word at a time. Two things make them stop and go back:

1. **Prediction fails.** They guessed what came next and were wrong ("The whole conversation is *eating*…" — conversations don't eat).
2. **Memory overflows.** They had to hold a subject in mind for too long before the verb arrived.

Every check below is one of those two costs. The goal is fewer re-reads, not shorter text and not "human-sounding" text.

## Why models write this way (so you know what to resist)

- **Confirmed (paper, Exp 1):** All nine frontier and near-frontier models tested use more inanimate-subject + animate-verb sentences and more rare word pairs than human text in the same genre. Most also use longer dependencies, more stacked nouns and more reduced object relatives in chat. A round-trip translation paraphrase with the same meaning removes much of it, so the meaning didn't require it.
- **Confirmed (paper, Exp 2):** RL with a length penalty pushed a small model (Qwen2.5-1.5B) to a near-categorical choice of the shorter option ("knew the answer was wrong" over "knew *that* the answer was wrong"). The preference also spread to constructions it was never trained on.
- **Inference (authors):** Rewards for correct answers, plus context-window limits, favour packing information densely over being understood. Effects are largest in long multi-turn chat and agentic coding. They are smaller in single-prompt essays.

So the bias to resist is **compression**: one clever verb where a plain clause would be clearer. Don't fight it with padding. A few extra words are worth spending when they save the reader a re-read.

## The governing rule: contextual, not categorical

In the paper, models turned a contextual human choice into a fixed rule ("always drop *that*"). Humans add an optional word when the next part is hard to predict, and leave it out when it isn't. **Doing the opposite on every sentence is the same mistake.** So:

- Fix a sentence only when a first-time reader would stall on it. Passing the **reread test** (below) is enough.
- Terms of art, conventional idioms and the venue's normal register stay. "The test fails", "the function returns", "the data show", "git stages changes" are conventional, so they are not findings.
- Don't touch quoted material, code, or wording that is clearly the author's own voice.
- Expect most sentences to pass. A clean draft gets zero edits.

## The checklist

Run it as a single pass while drafting, or as a review over a finished draft. Full worked examples quoted from the paper are in `references/examples.md`. Read it the first time you use this skill.

| # | Check | Cost | Stall signal | Fix |
|---|---|---|---|---|
| 1 | **Inanimate subject, animate verb** | prediction | A thing *expects, asks, promises, swallows, bites, misunderstands, eats, earns its keep* | Name the real actor ("you have to…") or the real effect ("causes an error"). If the literal phrase exists, use it. |
| 2 | **Subject-verb gap** | memory | More than ~7 words, or a whole clause or list, between the subject and its main verb | Get to the verb sooner. Move the list or modifier after the verb, put a heavy subject last, or split into two sentences. |
| 3 | **Dropped *that* / reduced relative** | prediction | The noun after the verb reads as its object until the sentence turns ("she knew the answer… was wrong") | Put back *that* (or *which/who*) where the next noun could be misread. Leave it out when the clause is short and obvious ("the book I read"). |
| 4 | **Stacked nouns (3+)** | prediction + memory | "class-time shutdown requirement", "absolute dotfile backup path handling" | Unstack with a verb or *of/for/that*: "requires phones to be off during class". Established compounds ("money market fund") stay. |
| 5 | **Ad-hoc noun → verb** | prediction | "footnote it", "calendar it", "categorize as speed-runnable" | Use the verb phrase: "put it in a footnote". Conventional ones stay (*email, bottle, stage, mask*). |
| 6 | **Coined or rare word pair** | prediction | A phrase the reader has never seen: "reader-patience budget", "gear trap", "lazy-intermediate Lookup behavior" | Use the common phrase. If you need the new term, define it once in plain words. If you can't unpack it yourself, the reader can't either: go back to the source or ask. |
| 7 | **Metaphor standing in for a literal** | prediction | The sentence makes sense only once the figure is decoded ("eating its own tail") | Say the literal thing ("going in circles"). Keep a metaphor only when it explains something the literal can't. |

Checks 1, 6 and 7 often show up in the same phrase. Count it once.

## Two self-tests (no other model needed)

- **Reread test.** Read the sentence as a stranger, one word at a time, and guess the next word at each step. If a guess fails and you have to go back to reparse, flag it. If you don't stall, it's fine, even when it's dense.
- **Plain-translation test** (adapted from the paper's round-trip method). Ask how a literal, unliterary translator would put the sentence into another language and back. If the result is clearer and only a few words longer, use it. *"Sometimes chaos expects you to remember it independently"* comes back as *"Sometimes you have to remember messy things on your own."*

The paper used round-trip translation as a measurement, not as a writing intervention. Using it as a writing check is this skill's inference and hasn't been tested.

## Operations

- **write** (default when drafting anything for a person): write normally, then do one pass with the checklist on the sentences that carry the main point: the answer, the conclusion, the instruction. Don't comment on the pass. Just deliver the cleaner text.
- **review**: diagnose only. For each finding: quote the sentence, give the check number, name the stall ("reader expects X, gets Y" or "holds N words before the verb"), and propose a rewrite. Report the count of sentences checked against sentences flagged. Make no edits.
- **revise**: run review first, then apply the fixes. Prefer replacing words over adding them. Keep the meaning, every fact and every number. Don't add hedges, claims or examples. Stop when the reread test passes, not when the text "sounds human".

## Guardrails

- **Don't invent to unpack.** Unpacking a compressed phrase must not add facts. If the plain version needs information the draft doesn't contain, flag it and leave it as is or ask.
- **No over-correction.** Don't add *that* everywhere, never stack nouns, or ban every metaphor. A draft where every optional word is restored has its own uniform, padded fingerprint. Aim for the human middle.
- **Density is allowed where readers expect it.** Changelogs, commit subjects, tables and expert-to-expert notes may stay clipped. Apply checks 2–6 lightly there. Checks 1 and 7 still apply.
- **Scope of the evidence.** The paper measured English only, with nine 2026 frontier models plus open-weight baselines, in chat, coding and essays. It ran no reader experiment. The processing costs come from prior psycholinguistics. For Chinese or other languages, the two costs (prediction, memory) still apply, but the specific rows are untested.
- **Not a humanizer.** This skill doesn't try to evade AI detectors or identify which model wrote a text. Use a dedicated de-AI skill (e.g. Sepia) for narrative structure, slop vocabulary or venue templates. Stack it after this one if you need both.
