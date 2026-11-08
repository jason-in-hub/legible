# Worked examples

The **Before** sentences are quoted verbatim from Clark, Martin & Mahowald (2026), arXiv:2610.29162: Table 2, Table 3, §1 and §3.1. Model names are as given in the paper. The **After** rewrites were written for this skill and don't come from the paper. Each one keeps the original's facts and adds none.

"Keep" rows matter as much as "fix" rows. They show where the checklist does **not** fire.

## 1 · Inanimate subject, animate verb

| Before | Stall | After |
|---|---|---|
| Sometimes chaos has a 1099; sometimes chaos expects you to remember it independently. *(GPT-5.6 Sol, chat)* | Chaos can't expect anything. | Sometimes the income comes with a 1099; sometimes you have to remember it on your own. |
| `is_file()` swallows that and returns False *(§3.1)* | Functions don't swallow. | `is_file()` catches that error and returns False. |
| Puzzle patterns where this asymmetry bites *(§3.1)* | Asymmetries don't bite. The paper glosses it as "causes an issue". | Puzzle patterns where this asymmetry causes a problem |
| Second, the time objection misunderstands how service actually functions. *(Kimi, essay)* | Objections don't understand; people do. | Second, people who object on time grounds misunderstand how service works. |
| A song doesn't ask you to turn melancholy into a calendar item. *(GPT-5.6 Terra, chat)* | Songs don't ask; "calendar item" is a check 6 pairing too. | With a song, you don't have to schedule time to feel sad. |
| The docstring promises they're skipped when they "appear anywhere in the source_dir path" *(Fable, coding)* | Mild: "promises" adds nothing that "says" doesn't. | The docstring says they're skipped when they "appear anywhere in the source_dir path" |
| **Keep:** The tests fail on the old code. | — | Conventional in code. No stall. |

## 2 · Subject-verb gap

| Before | Stall | After |
|---|---|---|
| The guitar sitting in the corner because you're still "deciding" teaches you zero chords. *(Sonnet, chat)* | Eight words to hold between *guitar* and *teaches*. | While you're still "deciding", the guitar sits in the corner. It teaches you zero chords there. |
| All five expression shapes — attribute access, subscript, calls, nested calls, string literals — leave `current` on `NAME('b')`, and the full template renders correctly. *(Fable, coding)* | A five-item list sits between the subject and the verb. | All five expression shapes leave `current` on `NAME('b')`, and the full template renders correctly. The five are attribute access, subscripts, calls, nested calls and string literals. |
| Class time, where a total blackout policy would apply under Policy 1, remains protected and focused. *(Sonnet, essay)* | A full clause sits inside the subject. | Class time stays protected and focused. Policy 1 would apply a total blackout there. |
| A lattice constructed with duplicate points, or a SymbolSet with colliding labels/names, can overwrite internal dictionary or attribute mappings. *(Terra, coding)* | The heavy subject comes first. | Two inputs can overwrite internal dictionary or attribute mappings: a lattice built with duplicate points, or a SymbolSet whose labels or names collide. |
| **Keep:** Has the building had water, mold, structural, or insurance claims? *(Luna, chat)* | The gap is short and the list is predictable. | Leave it. |

## 3 · Dropped *that* / reduced relative

| Before | Stall | After |
|---|---|---|
| (She) knew the answer was wrong *(Table 3, short variant)* | Reads as "knew the answer" until *was wrong* turns it around. | She knew **that** the answer was wrong. |
| …the unclosed-tag errors are the papercut people feel day-to-day. *(GLM, coding)* | Reduced relative + metaphor (check 7) + rare pair. | …the unclosed-tag errors are the ones **that** bother people every day. |
| Three fail on the old code; the others check behaviour the old code never reached. *(Opus 5.5, coding)* | Borderline: *behaviour the old code* briefly parses as a compound. | …the others check behaviour **that** the old code never reached. |
| **Keep:** That's not "trip to Vegas" money, that's "leave the job you hate" money. *(Kimi, chat)* | "the job you hate" is short and idiomatic. | Leave it. This is voice. |
| **Keep:** That's great for a beginner, honestly one of the best genres you could pick. *(Opus 5.5, chat)* | No misreading is possible. | Leave it. |

## 4 · Stacked nouns

| Before | Stall | After |
|---|---|---|
| I acknowledge concerns about distraction, but Policy 1's class-time shutdown requirement directly addresses this. *(Kimi, essay)* | Four nouns to bracket. | I acknowledge concerns about distraction, but Policy 1 addresses them directly: phones must be off during class. |
| Fixed absolute dotfile backup path handling while preserving the `:` marker used during reinstall. *(Luna, coding)* | Five-word stack. Which noun is the head? | Fixed how backups handle absolute dotfile paths, keeping the `:` marker that reinstall uses. |
| **Keep:** …brokerage money market funds (Fidelity's SPAXX, Vanguard's VMFXX) are the standard options. *(Opus 5, chat)* | "money market fund" is an established term. | Leave it. |
| **Keep:** …a community service honor cord at graduation. *(Fable, essay)* | Established US school term. | Leave it. |

## 5 · Ad-hoc noun → verb

| Before | Stall | After |
|---|---|---|
| …footnote it. *(§1)* · calendar it *(§3.1)* | The noun is used as a verb with no convention behind it. | …put it in a footnote. · put it on your calendar |
| Genuinely unsolicited advice: don't try to get her to categorize movies as speed-runnable or not. *(Sonnet, chat)* | "speed-runnable" is a coinage (check 6). | Unsolicited advice: don't try to get her to sort movies into ones that are fine at 1.5x and ones that aren't. |
| **Keep:** The `last_when` fallback is therefore not dead code; it is masking that inconsistency. *(Luna, coding)* | "mask" is a conventional verb in code. | Leave it. |
| **Keep:** Prevented Git dry runs from installing hooks or staging changes. *(Sol, coding)* | "stage" is git's own term. | Leave it. A changelog may stay clipped. |

## 6 · Coined or rare word pair

| Before | Stall | After |
|---|---|---|
| It's not necessary, but it's surprisingly useful—and not really a gear trap. *(Sol, chat)* | "gear trap" is unseen. | It's not necessary, but it's surprisingly useful, and it won't drag you into buying more gear. |
| The most substantive unfixed item is the existing xfailed lazy-intermediate Lookup behavior; … *(Terra, coding)* | "lazy-intermediate Lookup behavior" can't be unpacked from the text alone. | **Flag, don't guess.** Go back to the code and name the behaviour, e.g. "`Lookup` fails when <condition> (test marked xfail)". |
| **Keep:** That's a really legitimate concern, and honestly it's the part most internet advice glosses over. *(Fable, chat)* | "gloss over" is a common idiom. | Leave it. |

## 7 · Metaphor standing in for a literal

| Before | Stall | After |
|---|---|---|
| The whole conversation is eating its own tail. *(Claude, cited in the video walkthrough)* | You have to decode the figure. | The whole conversation keeps going in circles. |

## All at once

The paper opens with one sentence built to show every feature together (§1):

> *Your instinct is right; the convoluted sentence you are currently reading is quietly eating its own reader-patience budget — footnote it.*

- object relative "the … sentence you are currently reading" (3)
- inanimate subject + "eat" (1, 7)
- stacked nouns and a rare n-gram, "reader-patience budget" (4, 6)
- ad-hoc denominal verb, "footnote" (5)

**After:** Your instinct is right. This sentence is hard to read and wears out the reader's patience. Move it to a footnote.

The rewrite is eight words shorter, not longer. Being legible doesn't mean being wordier.
