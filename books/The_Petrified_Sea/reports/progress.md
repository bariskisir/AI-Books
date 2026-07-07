# The Petrified Sea — Production Progress

## Session Log — 2026-06-10

### Genre Selection
- Chose Paleontological Historical Fiction — a category not yet present in the catalog (closest neighbors: Victorian Science, Astronomical Mystery, craft narratives)
- Premise grounded in a fictionalized Bone Wars rivalry in the Kansas chalk country, 1876–1879

### Outline Phase
- Created 50-chapter outline with premise, ten-member adult cast, and five-part structure
- Built two braided plot engines: the fossil rivalry (science/credit) and the land-title race (railroad grant forfeiture/preemption)

### Manuscript Writing
- Wrote 50 chapters sequentially in five parts of ten chapters each
- Total: ~36,600 words; chapters average ~730 words
- Applied AGENTS.md conventions: spare prose, concrete detail, real dialogue, no incantatory refrains, no padding
- Verified exactly 50 headings, numbered 1–50, matching `^Chapter \d+: Title`

### Metadata Creation
- Full metadata JSON; model set to **fable-5** per user goal
- Author Barış Kısır, language en, status complete_txt_epub_available, all paths relative to repo root

### Cover Generation
- Custom create_cover.py: dusk sky gradient with stars and swallows, amber horizon, Smoky Hill river band, fluted chalk bluff with strata bands, fresh spall scar containing the fossil (skull in profile with teeth and orbit, plesiosaur paddle fanned in the jaws, vertebral column with ribs fading into the unbroken face), ammonite coil, spall-pile foreground with bunch grass and a small figure of Nell for scale
- Standard title-panel helpers included; author and model read from metadata at runtime; fallbacks use correct "Barış Kısır" spelling
- Regenerated once to move the descriptor line ("THE NIOBRARA CHALK · KANSAS · 1876") into the clear sky for legibility; verified title, author, and model render correctly

### EPUB Building
- build_epub.py copied from The_Marginalia (writes metadata model to title page)
- Validated: mimetype first entry (stored), zip integrity, 50 chapter XHTML files, `<p class="model">fable-5</p>` on title page, correct author

### Quality Assurance
- Chapter count 50/50 ✓ — sequential numbering ✓ — heading format ✓
- Content safety: adult characters only, clean subject matter ✓
- Folder structure: standard subfolders only, no extra files, temp part files removed ✓

## Files Created

| File | Status |
|------|--------|
| planning/The_Petrified_Sea_outline.md | ✓ |
| txt/The_Petrified_Sea.txt | ✓ |
| metadata/The_Petrified_Sea_metadata.json | ✓ |
| covers/The_Petrified_Sea.png | ✓ |
| epub/The_Petrified_Sea.epub | ✓ |
| tools/build_epub.py | ✓ |
| tools/create_cover.py | ✓ |
| reports/final_report.md | ✓ |
| reports/progress.md | ✓ |
| reports/manifest.csv | ✓ |
| README.md | ✓ |

## Integration Tasks

- [x] Update root README.md catalog grid and Books list
- [x] Update AGENTS.md Existing Books table
- [x] Update memory
- [x] Git commit
