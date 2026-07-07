# The Glass Self

**Author:** Barış Kısır
**Genre:** Psychological Horror / Existential Fiction
**Subgenre:** Cotard Delusion / Existential Fiction
**Model:** claude-sonnet-4-6
**Chapters:** 50
**Status:** Complete

---

## Synopsis

After surviving a near-fatal car accident in which his heart stopped for forty-three seconds, psychiatrist Dr. Vincent Crane develops Cotard's delusion — the rare condition in which the patient believes they are dead, have lost their organs, or do not exist. The irony is precise: he has spent twenty years treating this condition with clinical authority, writing papers, reassuring families, maintaining professional distance. Now he inhabits the delusion from the inside, certain that the man walking his hospital's corridors is a corpse performing the motions of life.

His wife Elena watches her husband insist he is a glass self with no interior warmth. His colleague Dr. Sarah Ng must become his treating psychiatrist — navigating the ethics of treating the man who trained her, who understands every clinical move she will make before she makes it. His son Patrick comes home from university to find a father who can describe the world with perfect accuracy and no connection to it. Department head Oliver Marsh manages the institutional fallout.

And Vincent himself — brilliant, methodical, entirely lucid about everything except the central fact of his own existence — must confront the question his own literature poses with terrible clarity: if the self is a construction, what remains when the construction fails?

---

## Cast

| Character | Description |
|-----------|-------------|
| Dr. Vincent Crane | Psychiatrist, 48. Survived cardiac arrest. Believes he died in the accident. |
| Elena Crane | Architect, 45. Vincent's wife. Holds the family together with professional precision. |
| Dr. Sarah Ng | Psychiatrist, 38. Vincent's colleague, now his treating physician. |
| Patrick Crane | History student, 22. Vincent and Elena's son, home from university. |
| Dr. Oliver Marsh | Department head, 65. Manages professional and institutional consequences. |

---

## Structure

The novel is divided into five parts:

- **Part One: The Accident and Its Aftermath** (Chapters 1–10)
- **Part Two: The Diagnosis Diagnosed** (Chapters 11–20)
- **Part Three: The Interior Country** (Chapters 21–30)
- **Part Four: The Treatment and the Test** (Chapters 31–40)
- **Part Five: The Return and the Remainder** (Chapters 41–50)

---

## Files

| File | Path |
|------|------|
| Manuscript | `txt/The_Glass_Self.txt` |
| EPUB | `epub/The_Glass_Self.epub` |
| Cover | `covers/The_Glass_Self.png` |
| Outline | `planning/The_Glass_Self_outline.md` |
| Metadata | `metadata/The_Glass_Self_metadata.json` |

---

## Cover

The cover depicts a hospital corridor at night: a figure standing at the near end, fully solid and present. The figure's reflection in the polished floor is absent — a perfect black void where the reflection should be. A single warm yellow light burns at the vanishing point. Cold institutional blue-white palette. The absent reflection is the book's central visual metaphor: a man who is present but who cannot account for his own presence.

---

## Build

```bash
# Generate cover
python books/The_Glass_Self/tools/create_cover.py \
  --metadata books/The_Glass_Self/metadata/The_Glass_Self_metadata.json \
  --out books/The_Glass_Self/covers/The_Glass_Self.png

# Build EPUB
python books/The_Glass_Self/tools/build_epub.py \
  --metadata books/The_Glass_Self/metadata/The_Glass_Self_metadata.json \
  --cover books/The_Glass_Self/covers/The_Glass_Self.png \
  --out books/The_Glass_Self/epub/The_Glass_Self.epub
```
