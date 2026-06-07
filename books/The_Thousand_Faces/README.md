# The Thousand Faces

**Author:** Barış Kısır
**Genre:** Psychological Suspense
**Subgenre:** Clinical Psychology / Paranoia Thriller
**Model:** claude-sonnet-4-6
**Chapters:** 50
**Status:** Complete

---

## Synopsis

Dr. Sonia Park is a clinical psychologist at the Harmon Institute, a private residential clinic in upstate New York. When medical director Dr. Marcus Webb introduces a new neurological treatment protocol — combining deep-brain stimulation with an experimental compound designed to lower limbic-cortical resistance — Sonia begins experiencing her patients' worst fears as vivid, physical intrusions: vertigo in the presence of a height-phobic patient, claustrophobia near another. She categorizes these episodes as extreme empathic resonance.

Then her patient Devin Chen falls to his death from the institute's fire escape, in exact circumstances matching a vision Sonia had during their last session.

Investigating quietly, she discovers that the protocol is not a treatment. It is a data-collection apparatus. The compound is a mirror-neuron activator that dissolves the cognitive boundary between clinician and patient, creating a synchronized neurological state that Veridian Cognitive Systems, a private research firm, purchases at premium rates. The patients are being driven toward their worst fears to produce the richest data. The clinicians are being used as amplifiers, without their knowledge or consent. Sonia herself has been part of the experiment since her first session with a protocol patient.

With colleagues compromised, the institution's exits closing, and her own perception increasingly uncertain — she cannot be sure which of her thoughts are hers and which were placed there — she must build a case that will survive both external scrutiny and her own altered mind.

---

## Cast

- **Dr. Sonia Park, 36** — Clinical psychologist, primary investigator
- **Dr. Marcus Webb, 55** — Medical director, architect of the Harmon Protocol
- **Devin Chen, 28** — Patient, height phobia, first death
- **Nurse Agatha Rourke, 50** — Senior ward nurse, keeper of six years of evidence
- **Dr. Liam Ferris, 42** — Sonia's colleague, ambivalent protocol participant
- **Calista Graves, 33** — Patient, former Veridian employee, Sonia's unlikely ally

---

## Files

| File | Path |
|------|------|
| Outline | `planning/The_Thousand_Faces_outline.md` |
| Manuscript | `txt/The_Thousand_Faces.txt` |
| EPUB | `epub/The_Thousand_Faces.epub` |
| Cover | `covers/The_Thousand_Faces.png` |
| Metadata | `metadata/The_Thousand_Faces_metadata.json` |

---

## Cover

The cover depicts a clinical observation room with a one-way mirror. On the viewer's side: the monitoring room, dark, institutional, its pillars framing the glass. On the far side: a room packed with dozens of identical calm faces, arrayed in clinical rows, all looking directly at the viewer. Cold institutional white and grey, blue fluorescent light. The viewer is simultaneously the observer and the observed.

---

## Build

```bash
# Generate cover
python books/The_Thousand_Faces/tools/create_cover.py \
  --metadata books/The_Thousand_Faces/metadata/The_Thousand_Faces_metadata.json \
  --out books/The_Thousand_Faces/covers/The_Thousand_Faces.png

# Build EPUB
python books/The_Thousand_Faces/tools/build_epub.py \
  --metadata books/The_Thousand_Faces/metadata/The_Thousand_Faces_metadata.json \
  --cover books/The_Thousand_Faces/covers/The_Thousand_Faces.png \
  --out books/The_Thousand_Faces/epub/The_Thousand_Faces.epub
```
