"""Dogfood: run legible's own checks (score.analyse) over this repo's README prose and list every hit.
Run with a python that has spaCy: python dogfood.py [files...]   (default: ../README.md README.md)"""
import pathlib
import re
import sys

import score

ROOT = pathlib.Path(__file__).resolve().parent
files = sys.argv[1:] or [str(ROOT.parent / "README.md"), str(ROOT / "README.md")]
for f in files:
    text = re.sub(r"<[^>]+>", "", pathlib.Path(f).read_text())
    a = score.analyse(text)
    print(f"== {pathlib.Path(f).name}: {a['words']:.0f} words, {a['sents']:.0f} sentences | "
          f"long gap={a['long_gap']:.0f} stacked nouns={a['stack']:.0f} reduced relatives={a['orc_red']:.0f} "
          f"comp 'that' omitted={a['comp_omit']:.0f}/{a['comp']:.0f} inanimate subject={a['inanim']:.0f}")
    for kind, sent in a["_hits"]:
        print(f"  [{kind}] {sent.strip()[:220]}")
