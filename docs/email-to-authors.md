# Draft: email to the paper's authors (for you to send)

**To:** thomas.hikaru.clark@nyu.edu, matias.martin@utexas.edu, kyle@utexas.edu (addresses as printed on the arXiv HTML page; check before sending)
**Subject:** Question about code/data for "Why is AI-generated language so hard to understand?" (arXiv:2610.29162)

Dear Dr. Clark, Dr. Martin, Dr. Mahowald,

I read your paper closely and built a small open-source writing skill on it (github.com/jason-in-hub/legible). It turns the six features you measured into a checklist a model can run on its own drafts. I ran a first A/B test of it, and I'm writing because I could not find a code or data link in the paper.

Two questions:
1. Do you plan to release the 14-model corpus (chat, coding, essay), the round-trip translation outputs, and the feature-extraction code (the spaCy rules and the inanimate-subject / denominal-verb classifier setup)? My own detectors are approximations with `en_core_web_sm`, so my numbers cannot be compared with yours.
2. Has any reader study (self-paced reading, reread rates, comprehension) been run or planned? I would like to test whether the constructions you identified change human reading time, and I'd rather not duplicate work.

I'm happy to share my eval harness and results in return. Thank you for the paper; the length-penalty experiment in particular was a clean way to test the mechanism.

Best regards,
Jason Mak
