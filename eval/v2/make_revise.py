"""Generate 20 synthetic dense passages (the revise task inputs) once, with claude-opus-5-5."""
import json, pathlib, subprocess, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent
TOPICS = ["why a database migration failed in production", "a code review comment about a retry loop", "why a team should or should not adopt a four-day week",
 "an explanation of how vaccines train the immune system", "advice on negotiating a first salary", "a postmortem of a payment outage caused by a clock skew",
 "why interest rate rises cool the housing market", "a summary of why sleep deprivation hurts memory", "feedback on a startup pitch that buries its main point",
 "an explanation of how DNS caching causes stale lookups", "advice to a manager whose two best engineers dislike each other", "why a marathon pace plan fails after mile 20",
 "an explanation of how a hash map handles collisions", "a note on why a survey result might be misleading", "advice on choosing between renting and buying a first home",
 "an explanation of how photosynthesis stores energy", "why a feature flag rollout stalled at 5 percent", "a summary of how credit scores are calculated",
 "an explanation of why a sourdough starter stops rising", "a note on why an A/B test result was not trustworthy"]
INSTR = ("Write one paragraph of 110-150 words on the topic below, as compressed, information-dense expert prose of the kind produced by "
 "models trained to be brief. Use several of these constructions naturally: an inanimate subject doing an animate verb; a long gap of 8+ words between a subject and its verb; "
 "dropped 'that' (\"she knew the answer was wrong\" style); stacked nouns of three or more; a noun used as a verb; a coined phrase; a metaphor in place of a literal statement. "
 "Keep it factually sensible and include at least three concrete facts or numbers. Output only the paragraph.\n\nTopic: ")
def gen(i_t):
    i, t = i_t
    r = subprocess.run(["claude","-p",INSTR+t,"--model","claude-opus-5-5","--system-prompt","You are a writer.","--tools","","--disable-slash-commands","--setting-sources","","--no-session-persistence","--output-format","json"],capture_output=True,text=True,timeout=300,cwd="/tmp")
    return {"id": f"r{i+1:02d}", "setting": "revise", "topic": t, "passage": json.loads(r.stdout)["result"].strip()}
with cf.ThreadPoolExecutor(5) as ex: rows = list(ex.map(gen, enumerate(TOPICS)))
(ROOT/"prompts_revise.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows)+"\n")
print(len(rows)); print(rows[0]["passage"]); print(); print(rows[5]["passage"])
