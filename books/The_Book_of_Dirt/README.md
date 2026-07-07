# The Book of Dirt

**Genre:** Eco-Literary  
**Author:** Barış Kısır  
**Status:** Complete (txt + epub)

## Overview

In a drought-scarred corner of rural Australia, soil scientist Dr. Thomas Winton arrives at a remote research station expecting routine field work. Instead, he discovers something impossible: the earth beneath his feet records the molecular signature of every living thing that has ever touched it. As he learns to read the soil, he uncovers a catastrophic environmental crime buried by a powerful developer who is draining the ancient aquifer for profit.

With the help of Ruby Djarragun, an Aboriginal elder whose people have known about the earth's memory for millennia, Winton must navigate threats, arson, and a legal system that is not ready for the truth. The drought breaks. The land floods. And the buried evidence rises to the surface.

The Book of Dirt is a literary meditation on memory, loss, and the slow intelligence of the earth.

## Characters

- **Dr. Thomas Winton** — Soil scientist. Recently divorced. Meticulous, skeptical, haunted. He came to study soil degradation and found a mystery no peer-reviewed paper could explain.
- **Ruby Djarragun** — Aboriginal elder of the Yinhawangka people. In her seventies. She carries the old knowledge: the earth has a voice, a memory, a song.
- **Marcus Holloway** — CEO of Meridian Agricultural Holdings. Polished, ruthless, well-connected. He sees the drought as a business opportunity.
- **Dr. Elena Vasquez** — Hydrologist. Pragmatic, careful, drawn reluctantly into Winton's obsession.
- **Constable Danny Kettering** — Local police officer. Grew up in the drought country. His loyalties are tested.

## Files

| File | Path |
|------|------|
| Manuscript | `The_Book_of_Dirt/txt/The_Book_of_Dirt.txt` |
| EPUB | `The_Book_of_Dirt/epub/The_Book_of_Dirt.epub` |
| Cover | `The_Book_of_Dirt/covers/The_Book_of_Dirt.png` |
| Outline | `The_Book_of_Dirt/planning/The_Book_of_Dirt_outline.md` |
| Metadata | `The_Book_of_Dirt/metadata/The_Book_of_Dirt_metadata.json` |

## Build

To regenerate the EPUB from the manuscript:

```bash
python3 tools/build_epub.py --metadata metadata/The_Book_of_Dirt_metadata.json --cover covers/The_Book_of_Dirt.png --out epub/The_Book_of_Dirt.epub
```

To regenerate the cover:

```bash
python3 tools/create_cover.py --metadata metadata/The_Book_of_Dirt_metadata.json --out covers/The_Book_of_Dirt.png
```
