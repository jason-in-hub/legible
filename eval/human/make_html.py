"""Inline stimuli.json into spr_template.html -> index.html (single file; host on GitHub Pages / Netlify / Pavlovia)."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parent
t = (R / "spr_template.html").read_text()
s = json.loads((R / "stimuli.json").read_text())
slim = [{"id": x["id"], "orig": x["orig"], "placebo": x["placebo"], "skill": x["skill"], "questions": x["questions"]} for x in s]
(R / "index.html").write_text(t.replace("/*STIMULI*/[]", json.dumps(slim, ensure_ascii=False)))
print("index.html:", len(slim), "passages")
