# The Murmuration

**Genre:** Literary Thriller / Environmental Thriller  
**Author:** Barış Kısır  
**Status:** Complete (txt + epub)

## Overview

Saskia Vance, a wildlife photographer shattered by a near-fatal accident, retreats to the Somerset Levels to document starling murmurations. What she finds in the birds' flight patterns defies explanation: deliberate geometric formations carrying encoded data.

With the help of Dr. Alistair Naylor, an aging ornithologist, Saskia uncovers a conspiracy involving Aethelred Technologies — a data brokerage using the starlings as a biological communication network. The birds have been trained to carry falsified environmental reports, hiding decades of industrial pollution.

## Characters

- **Saskia Vance** — Wildlife photographer. Recovering from a climbing accident that killed her partner. Sharp, stubborn, observant.
- **Dr. Alistair Naylor** — Ornithologist, late sixties. Has spent forty years studying the starlings of the Somerset Levels.
- **The Collector (Marcus Sterling)** — Aethelred Technologies fixer. Former MI5. Polished and ruthless.

## Files

| File | Path |
|------|------|
| Manuscript | `The_Murmuration/txt/The_Murmuration.txt` |
| EPUB | `The_Murmuration/epub/The_Murmuration.epub` |
| Cover | `The_Murmuration/covers/The_Murmuration.png` |
| Outline | `The_Murmuration/planning/The_Murmuration_outline.md` |
| Metadata | `The_Murmuration/metadata/The_Murmuration_metadata.json` |

## Build

```bash
# Generate cover
python3 "The_Murmuration/tools/create_cover.py" \
  --metadata "The_Murmuration/metadata/The_Murmuration_metadata.json" \
  --out "The_Murmuration/covers/The_Murmuration.png"

# Build EPUB
python3 "The_Murmuration/tools/build_epub.py" \
  --metadata "The_Murmuration/metadata/The_Murmuration_metadata.json" \
  --cover "The_Murmuration/covers/The_Murmuration.png" \
  --out "The_Murmuration/epub/The_Murmuration.epub"
```
