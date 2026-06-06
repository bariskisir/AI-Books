# The Watcher on the Wall

**Genre:** Military Sci-Fi  
**Author:** Barış Kısır  
**Status:** Complete (txt + epub available)

## Synopsis

Private Elias Kane requested the most remote posting in human space. He got it: The Spire, a fortress of black ice on the frozen planet Ostrac, where he stands watch on the Wall, scanning the Barrens for signs of the Hush — an alien species that has been silent for fourteen years.

But when supplies spoil overnight, soldiers whisper in dead languages, and shadows move against the light, Kane begins to suspect the enemy is no longer outside the walls. It is already inside. And it has been waiting.

As the fortress descends into paranoia and the mimic threat spreads through the structure, Kane must confront a truth that will cost him everything: the walls that were meant to keep the enemy out were actually keeping something in.

## Contents

- `txt/The_Watcher_on_the_Wall.txt` — Full manuscript, 50 chapters
- `epub/The_Watcher_on_the_Wall.epub` — EPUB 3 ebook with cover
- `covers/The_Watcher_on_the_Wall.png` — Cover artwork
- `metadata/The_Watcher_on_the_Wall_metadata.json` — Metadata and descriptions
- `planning/The_Watcher_on_the_Wall_outline.md` — Chapter-by-chapter outline
- `tools/` — Utility scripts for building EPUB and generating covers
- `reports/` — Project reports

## Characters

- **Private Elias Kane** — A sharp-eyed but haunted soldier. He watches. He notices. He trusts no one.
- **Commander Marcus Holt** — Veteran of the last Hush war. Rigid, respected, burdened by what he knows.
- **The Entity** — The Hush central node. An infiltrator that learns, mimics, and replaces.
- **Corporal Reyes** — A field surgeon who survives the collapse and becomes Kane's ally.

## Build Commands

Generate cover:
```
python3 The_Watcher_on_the_Wall/tools/create_cover.py --metadata The_Watcher_on_the_Wall/metadata/The_Watcher_on_the_Wall_metadata.json --out The_Watcher_on_the_Wall/covers/The_Watcher_on_the_Wall.png
```

Build EPUB:
```
python3 The_Watcher_on_the_Wall/tools/build_epub.py --metadata The_Watcher_on_the_Wall/metadata/The_Watcher_on_the_Wall_metadata.json --cover The_Watcher_on_the_Wall/covers/The_Watcher_on_the_Wall.png --out The_Watcher_on_the_Wall/epub/The_Watcher_on_the_Wall.epub
```
