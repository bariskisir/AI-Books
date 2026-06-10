# AGENTS.md — AI-Books Project

This file defines conventions, structure, and rules for AI agents working on the AI-Books repository. Read this before any book-writing session.

## Project Overview

AI-Books is a proprietary English-language fiction project producing original novels. Each book is a standalone work in its own directory, following a consistent structure modeled on `The_Bellweather_Murders`.

**Goal:** 150+ complete novels, one per session.

## Directory Structure (per standalone book)

Standalone books live under `books/Book_Title/`. `The_Meridian_Cycle/` is the only series folder and may contain multiple book files. Every standalone book must use exactly this structure: no extra top-level folders, no extra files inside the standard subfolders, and no committed cache folders such as `__pycache__/`.

```
books/Book_Title/
├── planning/
│   └── Book_Title_outline.md       # 50-chapter outline
├── txt/
│   └── Book_Title.txt              # Full manuscript
├── epub/
│   └── Book_Title.epub             # EPUB export
├── covers/
│   └── Book_Title.png              # Cover image
├── metadata/
│   └── Book_Title_metadata.json    # Production metadata
├── reports/
│   ├── final_report.md
│   ├── manifest.csv
│   └── progress.md
├── tools/
│   ├── build_epub.py               # Copy from template, adjust series line
│   └── create_cover.py             # Custom per book (different imagery)
└── README.md                       # Per-book README
```

## Book Production Protocol

When the user asks for a new book or multiple new books, produce complete standalone books, not drafts. Follow this sequence for each book:

1. Choose a fresh title and genre that do not duplicate an existing book directory.
2. Create the exact standalone directory structure shown above.
3. Write `planning/Book_Title_outline.md` first with a premise, adult core cast, and a 50-chapter plan.
4. Write `txt/Book_Title.txt` with exactly 50 chapter headings matching `Chapter N: Title`, numbered 1 through 50 in order.
5. Create full metadata before packaging. The metadata `model` field is the single source of truth for model labeling.
6. Copy/adapt `tools/build_epub.py` from a recent complete book that already writes the metadata `model` field to the EPUB title page.
7. Write a custom `tools/create_cover.py` for that specific book, regenerate the PNG cover, then build the EPUB.
8. Write the per-book README and reports, update the root README catalog and Books list, update AGENTS.md's Existing Books table when appropriate, then commit.

Do not leave partially packaged books. A book is complete only when the outline, TXT, EPUB, cover PNG, metadata, reports, tools, per-book README, root README entries, and validation all exist.

### Model Labeling
- Every book metadata JSON must include a `model` field.
- The cover must read the model from metadata at runtime and print it at the bottom of the cover panel, below the author line. Do not hardcode the displayed model in the image; use `metadata.get("model", "")`.
- The EPUB title page must also display the same metadata model value, using the same pattern as recent completed books: `<p class="model">...</p>` in `OEBPS/text/title.xhtml`.
- If the user specifies a model label such as `gpt-5.5`, set `metadata["model"]` to that exact value and regenerate both the cover and EPUB.

### Cover Specificity
- Covers must be book-specific, not generic templates with only a changed title. Each `create_cover.py` should contain imagery designed for that book's premise, genre, setting, and mood.
- Prefer separate drawing functions and scene elements that name or clearly imply the book's subject: e.g., observatory domes for an astronomy mystery, court/harbor forms for a maritime legal mystery, ledgers and rain lines for an agricultural finance thriller.
- Do not reuse the same composition across a batch with only palette or title changes. Shared standard title-panel helpers are allowed; the upper artwork must be distinct.
- The cover must include the book title, the author name from metadata, and the metadata model label at the bottom.
- After editing `create_cover.py`, always regenerate the PNG and visually or programmatically verify that the title, author, and model are present.

### Completion Checks
- Verify each TXT has exactly 50 chapter headings, numbered 1-50.
- Verify every standalone book folder contains only the standard top-level structure and only the expected file inside each standard subfolder.
- Verify metadata author is exactly `Barış Kısır`, language is `en`, status is `complete_txt_epub_available`, and all paths are relative to repo root.
- Verify the EPUB opens as a valid ZIP, contains `mimetype` first, has chapter XHTML files, and has the model on the title page.
- Verify the cover script contains the standard title-panel helpers, reads author/model from metadata, and the generated PNG is non-empty and unique for that book.

## Writing Conventions

### Prose Style
- **Literary but spare** — concrete detail, real dialogue, short sentences.
- **No incantatory refrains** — do not repeat a lyrical phrase across a chapter or book. The model degenerates into filler loops when lyrical refrains are used (the "repetition-recursion" pitfall).
- **Chapters:** 700–1,500 words ideal. Never pad for word count.
- **Show, don't tell** — use sensory detail, action, and dialogue over exposition.
- **Dialogue** with proper attribution. Characters should sound distinct.

### Content Safety
- **Adult characters only.** No minors in sexual or abusive contexts.
- **Clean subject matter.** No sexual abuse, no exploitation of minors.
- Avoid gratuitous violence. Handle dark themes with literary restraint.

### Chapter Formatting (required for EPUB build script)
```
Chapter 1: Chapter Title

Content here. Paragraphs separated by blank lines.
```
The build script (`build_epub.py`) uses the regex `^Chapter\s+(\d+):\s+(.+)$` to split chapters. Every heading must match exactly; do not add alternate heading patterns such as `Bölüm`.

## Build Pipeline

1. **Write** the manuscript to `txt/Book_Title.txt`
2. **Generate cover:** `python3 tools/create_cover.py --metadata metadata/... --out covers/...`
3. **Build EPUB:** `python3 tools/build_epub.py --metadata metadata/... --cover covers/... --out epub/...`
4. **Update the `## Books` list** in `README.md` — append a new `<details>` block at the end of the list (before the License section) with cover image, read-online link, and EPUB download link. Newest book always goes last.
5. **Update the Catalog grid** at the top of `README.md` — add the new book's thumbnail to the HTML `<table>` (5 covers per row, 150px wide each). Insert the new `<td>` entry before the closing `</table>` tag as part of the existing last row or as a new `<tr>` row.
6. **Commit** all files with a descriptive message.

### Cover Convention
- **No "A Novel of" subtitle line.** Do not include "A Novel of" or "A Novel of the" text on covers. Location/descriptor lines (e.g., "LARKLIGHT POINT", "ANTARCTIC DARK") are fine and should stay.
- **Author name on covers MUST be "Barış Kısır"** with correct Turkish characters (ş = U+015F, ı = U+0131). Never use ASCII-only "Baris Kisi" or "Baris Kisir".
- Always read the author name from the metadata JSON at runtime (`metadata.get("author", "Barış Kısır")`) rather than hardcoding. Every fallback in the script must use the correct Turkish spelling.
- Verify the cover renders the correct author name after generation — if it shows "BARIS KISI" instead of "BARIŞ KISIR", fix the script and regenerate.

### Tool Setup
- Copy `build_epub.py` and `create_cover.py` from an existing book into the new book's `tools/` directory.
- Edit the `series` line in `build_epub.py` to use the book directory slug with underscores, e.g. `The_Quiet_Room`.
- Rewrite `create_cover.py` with imagery appropriate to the new book (different landscape, mood, palette). Use PIL to draw unique shapes, gradients, and lighting for each book's theme.
- The cover script must end with these standard helpers (they render the title/author panel at the bottom):
  - `_standard_cover_font`, `_standard_cover_repair_text`, `_standard_cover_wrap`, `_standard_cover_center`, `_standard_cover_title_font`, `_standard_cover_resolve_title`, `_standard_cover_resolve_author`, `_draw_standard_cover_title_panel`
- After writing the script, regenerate the cover even if you think it's correct — this catches any hardcoded wrong author name.

## Outline Convention

Each outline should have:
- **Premise** (1 paragraph)
- **Core Cast** (listed with brief descriptions)
- **50 Chapter Plan** (each with a 1-line summary in present tense)

Structure the chapters in natural parts/acts (roughly 10 chapters each, though not rigid). Outline first, write after.

## Book Metadata

Always populate `metadata/` JSON with:
- `title`, `author` (always "Barış Kısır"), `genre`, `subgenre`
- `language`: "en"
- `short_description` (1 sentence), `long_description` (2-3 paragraphs)
- `main_characters` (list)
- `keywords` (list)
- All paths relative to repo root
- `status`: "planned" → "complete_txt_epub_available"

## Memory

Project-level instructions and progress live at:
`C:\Users\white\.claude\projects\C--Users-white-main-gitrepos-AI-Books\memory\`

The key file is `ai-books-project.md` which tracks completed books and the repetition-recursion safety constraint.

## Existing Books

Books are listed in order of addition — oldest first, newest last. Always append new books to the end.

| Directory | Genre | Chapters | Status |
|-----------|-------|----------|--------|
| `books/The_Bellweather_Murders/` | Crime / Small-town murder mystery | 50 | Complete |
| `books/The_Meridian_Cycle/` | Sci-fi series (10 books) | 50 each | Complete |
| `books/Larklight/` | Literary fiction / Family saga | 50 | Complete |
| `books/The_Wintering/` | Literary fiction / Historical survival | 50 | Complete |
| `books/The_Salt_Road/` | Literary fiction / Contemporary family drama | 50 | Complete |
| `books/The_Long_Exposure/` | Literary fiction / Quiet mystery (science & memory) | 50 | Complete |
| `books/The_Marigold_Express/` | Comic crime / Ensemble heist caper | 50 | Complete |
| `books/The_Dust_Horizon/` | Western / Frontier revenge saga | 50 | Complete |
| `books/The_Quiet_Room/` | Psychological thriller / Sensory deprivation suspense | 50 | Complete |
| `books/Love_in_Aisle_Five/` | Romantic comedy / Workplace romance | 50 | Complete |
| `books/Briar_House/` | Gothic horror / Haunted house | 50 | Complete |
| `books/The_Vienna_Exchange/` | Cold War spy thriller / Espionage | 50 | Complete |
| `books/The_Last_Orchard/` | Post-apocalyptic / Survival | 50 | Complete |
| `books/The_Burden_of_Proof/` | Legal thriller / Courtroom drama | 50 | Complete |
| `books/The_Meridian_Door/` | Portal fantasy / Alternate world | 50 | Complete |
| `books/The_Iron_Coast/` | Historical adventure / Pirate swashbuckling | 50 | Complete |
| `books/The_Unfortunate_Mr_Quill/` | Dark comedy / Satire mistaken identity | 50 | Complete |
| `books/The_Ember_Throne/` | Epic Fantasy | 50 | Complete |
| `books/Neon_Saints/` | Cyberpunk | 50 | Complete |
| `books/The_Last_Migration/` | Dystopian | 50 | Complete |
| `books/The_Time_Binders_Apprentice/` | Time Travel | 50 | Complete |
| `books/Silver_and_Bone/` | Urban Fantasy | 50 | Complete |
| `books/The_Star_Crossed_Engine/` | Steampunk | 50 | Complete |
| `books/The_Hound_of_Blackwood_Lane/` | Cozy Mystery | 50 | Complete |
| `books/The_Seventh_Precinct/` | Noir | 50 | Complete |
| `books/The_Cinder_Queen/` | Dark Fantasy | 50 | Complete |
| `books/Ghost_Fleet_Armada/` | Space Opera | 50 | Complete |
| `books/The_Ambassadors_Shadow/` | Political Thriller | 50 | Complete |
| `books/The_Bone_Garden/` | Medical Thriller | 50 | Complete |
| `books/Zero_Day_Protocol/` | Techno-Thriller | 50 | Complete |
| `books/The_Lost_Colony/` | Historical Fiction | 50 | Complete |
| `books/The_Silk_Road_Deception/` | Historical Thriller | 50 | Complete |
| `books/The_Kaisers_Watch/` | Alternate History | 50 | Complete |
| `books/Red_Phoenix_Rising/` | Superhero | 50 | Complete |
| `books/The_Hollow_Men/` | Supernatural Thriller | 50 | Complete |
| `books/The_Ash_Garden/` | Literary Fiction | 50 | Complete |
| `books/The_Cartographers_Daughter/` | Adventure | 50 | Complete |
| `books/Beneath_the_Glass_Sea/` | Climate Fiction | 50 | Complete |
| `books/The_Mourning_Doves/` | Gothic Romance | 50 | Complete |
| `books/The_Parachute_Regiment/` | War Drama | 50 | Complete |
| `books/The_Oracles_Lament/` | Mythological Fiction | 50 | Complete |
| `books/The_Night_Market/` | Magical Realism | 50 | Complete |
| `books/The_God_Game/` | Religious Thriller | 50 | Complete |
| `books/The_Rust_Maiden/` | Dieselpunk | 50 | Complete |
| `books/The_Still_Point/` | Literary Fiction | 50 | Complete |
| `books/The_Mountain_Will_Not_Fall/` | Survival Thriller | 50 | Complete |
| `books/The_Children_of_the_Flood/` | Science Fiction | 50 | Complete |
| `books/The_Clockwork_Rabbi/` | Historical Fantasy | 50 | Complete |
| `books/Dandelion_Wine_Summer/` | Coming of Age | 50 | Complete |
| `books/The_Echo_Chamber/` | Satire | 50 | Complete |
| `books/The_Upper_Room/` | Ghost Story | 50 | Complete |
| `books/The_Deep_Between_Stars/` | Oceanic Horror | 50 | Complete |
| `books/The_Moscow_Protocol/` | Spy Thriller | 50 | Complete |
| `books/The_Perfect_Neighbor/` | Domestic Thriller | 50 | Complete |
| `books/The_Ice_Below/` | Arctic Thriller | 50 | Complete |
| `books/The_Garden_of_Unearthly_Delights/` | Biopunk | 50 | Complete |
| `books/The_Witch_of_Thornwood_Hollow/` | Fantasy Romance | 50 | Complete |
| `books/The_Lost_Aisle/` | Academic Mystery | 50 | Complete |
| `books/The_Palermo_Exchange/` | Crime Thriller | 50 | Complete |
| `books/The_Safe_House/` | Romantic Suspense | 50 | Complete |
| `books/The_Crimson_Waste/` | Sword and Sorcery | 50 | Complete |
| `books/The_Gaslight_Grimoire/` | Gaslamp Fantasy | 50 | Complete |
| `books/The_Candidates_Wife/` | Political Satire | 50 | Complete |
| `books/The_Long_Count/` | Sports Drama | 50 | Complete |
| `books/The_Glass_Shoe/` | Fairy Tale Retelling | 50 | Complete |
| `books/The_Thirty_Seventh_Floor/` | Conspiracy Thriller | 50 | Complete |
| `books/The_Last_Telegram/` | Literary Fiction | 50 | Complete |
| `books/The_Last_Picture_House/` | Small Town Fiction | 50 | Complete |
| `books/The_Wolves_of_Winter/` | Prehistoric Survival | 50 | Complete |
| `books/The_Book_of_Dirt/` | Eco-Literary | 50 | Complete |
| `books/The_Ocean_Waits/` | Slow-Burn Horror | 50 | Complete |
| `books/The_Dead_Letter_Office/` | Epistolary Mystery | 50 | Complete |
| `books/The_Mermaids_Tear/` | Oceanic Adventure | 50 | Complete |

| `books/The_Sapphire_Throat/` | Jazz Age Crime | 50 | Complete |
| `books/The_Last_Lighthouse/` | Dystopian Survival | 50 | Complete |
| `books/The_Winter_Orchid/` | Dark Academia | 50 | Complete |
| `books/Paper_Tigers/` | Contemporary Fiction | 50 | Complete |
| `books/The_Fifth_Season/` | Literary Romance | 50 | Complete |
| `books/The_Ghost_Bridge/` | Cosmic Horror | 50 | Complete |
| `books/The_Clockmakers_War/` | Militaristic Fantasy | 50 | Complete |
| `books/The_Depth_of_Summer/` | Coming of Age | 50 | Complete |
| `books/The_Drowned_Bells/` | Coastal Gothic | 50 | Complete |
| `books/Red_Weather/` | Climate Thriller | 50 | Complete |
| `books/The_Seventh_Chamber/` | Historical Mystery | 50 | Complete |
| `books/The_Ferrymans_Daughter/` | Mythic Fantasy | 50 | Complete |
| `books/The_Bee_Thief/` | Rural Noir | 50 | Complete |
| `books/The_Glass_Maker/` | Historical Fiction | 50 | Complete |
| `books/The_Last_Tram/` | Slipstream | 50 | Complete |
| `books/The_Velvet_Underground/` | Music Fiction | 50 | Complete |
| `books/The_Alchemists_Wife/` | Tudor Historical | 50 | Complete |
| `books/The_Last_Taxi/` | Urban Magical Realism | 50 | Complete |
| `books/The_Radio_Operator/` | War Romance | 50 | Complete |
| `books/The_Orchid_Thief_of_Calcutta/` | Colonial Adventure | 50 | Complete |
| `books/The_Bitter_Wind/` | Arctic Survival | 50 | Complete |
| `books/The_Calligraphers_Secret/` | Literary Historical | 50 | Complete |
| `books/The_Abandoned_Station/` | Post-Apocalyptic | 50 | Complete |
| `books/The_Noise_Between_Stars/` | Hard Sci-Fi | 50 | Complete |
| `books/The_Hireling/` | Historical Noir | 50 | Complete |
| `books/The_Dark_Between_Stars/` | Lovecraftian | 50 | Complete |
| `books/The_Photographers_Wife/` | Postwar Literary | 50 | Complete |
| `books/The_Jade_Dragon/` | Wuxia Fantasy | 50 | Complete |
| `books/The_Ballroom_of_Shadows/` | Gothic Mystery | 50 | Complete |
| `books/The_Bookbinder_of_Prague/` | WWII Historical | 50 | Complete |
| `books/The_Half_Life_of_Love/` | Science Romance | 50 | Complete |
| `books/The_Last_Caravan/` | Historical Adventure | 50 | Complete |
| `books/The_Ghost_of_the_Grand_Hotel/` | Haunted House | 50 | Complete |
| `books/The_Whaling_Wife/` | Nautical Historical | 50 | Complete |
| `books/The_Train_in_the_Snow/` | Winter Mystery | 50 | Complete |
| `books/The_Garden_of_Forgotten_Things/` | Magical Realism | 50 | Complete |
| `books/The_Mermaid_of_Monhegan/` | Coastal Literary | 50 | Complete |
| `books/The_Hotel_at_the_End_of_the_World/` | Surreal Fiction | 50 | Complete |
| `books/The_Botanists_Daughter/` | Family Drama | 50 | Complete |
| `books/The_Glass_Prison/` | Prison Thriller | 50 | Complete |
| `books/The_Carnival_at_Midnight/` | Weird Fiction | 50 | Complete |
| `books/The_Piano_Tuner/` | Literary Gothic | 50 | Complete |
| `books/The_Last_Hunt/` | Western Literary | 50 | Complete |
| `books/The_Astronomers_Daughter/` | Victorian Science | 50 | Complete |
| `books/The_Street_of_Many_Doors/` | Sliding Doors | 50 | Complete |
| `books/The_Lighthouse_at_the_End/` | Psychological Horror | 50 | Complete |
| `books/The_Broken_Hour/` | Time Loop | 50 | Complete |
| `books/The_Salt_Wife/` | Folk Horror | 50 | Complete |
| `books/The_Winter_Garden/` | Dual Timeline | 50 | Complete |
| `books/The_Elevator/` | High-Stakes Thriller | 50 | Complete |
| `books/The_Tobacco_Fields_of_Virginia/` | Southern Gothic | 50 | Complete |
| `books/The_Thief_of_Small_Things/` | Quirky Fiction | 50 | Complete |
| `books/The_Fourth_Wall/` | Metafiction | 50 | Complete |
| `books/The_Black_Swan/` | Ballet Fiction | 50 | Complete |
| `books/The_Mapmakers_Dream/` | Exploration Fiction | 50 | Complete |
| `books/The_Watcher_on_the_Wall/` | Military Sci-Fi | 50 | Complete |
| `books/The_Beekeepers_War/` | WWI Literary | 50 | Complete |
| `books/The_House_of_Many_Windows/` | Architectural Thriller | 50 | Complete |
| `books/The_Last_Rose_of_Summer/` | Romantic Drama | 50 | Complete |
| `books/The_Iron_Lung/` | Medical Drama | 50 | Complete |
| `books/The_Library_of_Dreams/` | Metaphysical Fiction | 50 | Complete |
| `books/The_Last_Pharaohs_Secret/` | Ancient Historical | 50 | Complete |
| `books/The_Cold_Water/` | Debut Novel | 50 | Complete |
| `books/The_Bridge_of_Sighs/` | Venetian Mystery | 50 | Complete |
| `books/The_House_on_the_Cliff/` | Domestic Suspense | 50 | Complete |
| `books/The_Factory_of_Smiles/` | Dystopian Satire | 50 | Complete |
| `books/The_Horse_Whisperers_Daughter/` | Rural Fiction | 50 | Complete |
| `books/The_Woman_in_the_Window/` | Neo-Noir | 50 | Complete |
| `books/The_Last_Cowboy/` | Contemporary Western | 50 | Complete |
| `books/The_Song_of_the_Whale/` | Nature Writing | 50 | Complete |
| `books/The_Porcelain_Doll/` | Japanese Literary | 50 | Complete |
| `books/The_Devils_Trombone/` | Jazz Fiction | 50 | Complete |
| `books/The_Lighthouse_Keepers_Wife/` | Historical Romance | 50 | Complete |
| `books/The_Miracle_of_Saint_Johns/` | Inspirational Fiction | 50 | Complete |
| `books/The_Truth_About_Monsters/` | Children's Fantasy | 50 | Complete |
| `books/The_Black_Tulip/` | Historical Romance | 50 | Complete |
| `books/The_Vanishing_of_Eleanor_Rigby/` | Psychological Mystery | 50 | Complete |
| `books/The_Emperors_Nightingale/` | Fairytale Fantasy | 50 | Complete |
| `books/The_Kitchen_Witch/` | Cozy Fantasy | 50 | Complete |
| `books/The_River_Mother/` | Magical Realism | 50 | Complete |
| `books/The_Last_Shot/` | Tennis Drama | 50 | Complete |
| `books/The_Blue_Hotel/` | Suspense Western | 50 | Complete |
| `books/The_Watermelon_Summer/` | Southern Fiction | 50 | Complete |
| `books/The_Man_Who_Forgot_His_Wife/` | Amnesia Thriller | 50 | Complete |
| `books/The_Murmuration/` | Literary Thriller | 50 | Complete |
| `books/The_Understudy/` | Theatrical Suspense | 50 | Complete |
| `books/The_Body_in_the_Library/` | Classic Whodunit | 50 | Complete |
| `books/The_Last_Silk_Dress/` | Gilded Age Fiction | 50 | Complete |
| `books/The_Last_Job/` | Heist Noir | 50 | Complete |
| `books/The_Milkmans_Son/` | Irish Literary | 50 | Complete |
| `books/The_Last_Voyage_of_the_Mermaid/` | Nautical Horror | 50 | Complete |
| `books/The_Vegetarians_Wife/` | Psychological Literary | 50 | Complete |
| `books/The_Music_Box/` | Psychological Suspense | 50 | Complete |
| `books/The_Mona_Lisa_Smile/` | Art Mystery | 50 | Complete |
| `books/The_White_Raven/` | Nordic Noir | 50 | Complete |
| `books/The_Saffron_Kitchen/` | Culinary Mystery | 50 | Complete |
| `books/The_Glass_Cockpit/` | Aviation Thriller | 50 | Complete |
| `books/The_Bone_Orchard_Trail/` | Weird West | 50 | Complete |
| `books/The_Iron_Whale/` | Submarine Thriller | 50 | Complete |
| `books/The_Gilded_Menagerie/` | Circus Historical | 50 | Complete |
| `books/The_Eighth_Summit/` | Mountaineering Drama | 50 | Complete |
| `books/The_Tin_Soldiers_Waltz/` | Whimsical Fantasy | 50 | Complete |
| `books/The_Memory_Merchant/` | Speculative Fiction | 50 | Complete |
| `books/The_Constant_Garden/` | Eco-Utopia | 50 | Complete |
| `books/The_Unwritten_City/` | Political Utopia | 50 | Complete |
| `books/The_Glass_Concord/` | Transparency Utopia | 50 | Complete |
| `books/The_Fair_Exchange/` | Economic Utopia | 50 | Complete |
| `books/The_Long_Truce/` | Pacifist Utopia | 50 | Complete |
| `books/The_Harmony_Engine/` | Algorithmic Utopia | 50 | Complete |
| `books/The_Open_Gate/` | Borderless Utopia | 50 | Complete |
| `books/The_Common_Breath/` | Resource Utopia | 50 | Complete |
| `books/The_Perennial/` | Immortality Utopia | 50 | Complete |
| `books/The_Witness/` | Memory Utopia | 50 | Complete |
| `books/The_Architects_Dream/` | Designed Utopia | 50 | Complete |
| `books/The_Seed_Ark/` | Generation Ship Utopia | 50 | Complete |
| `books/The_Reversal/` | Psychological Thriller | 50 | Complete |
| `books/The_Whispering_Gallery/` | Gothic Mystery | 50 | Complete |
| `books/The_Lantern_Index/` | Literary Mystery / Archival Suspense | 50 | Complete |
| `books/The_Atlas_of_Lost_Worlds/` | Fantasy | 50 | Complete |
| `books/The_Falconers_Knot/` | Medieval Mystery | 50 | Complete |
| `books/The_Copper_Saint/` | Renaissance Thriller | 50 | Complete |
| `books/The_Driftwood_Court/` | Coastal Legal Mystery | 50 | Complete |
| `books/The_Rainmakers_Ledger/` | Financial Thriller | 50 | Complete |
| `books/The_Silent_Observatory/` | Astronomical Mystery | 50 | Complete |
| `books/The_Harvest_of_Ashes/` | Agrarian Dystopia | 50 | Complete |
| `books/The_Gilded_Ferry/` | Victorian Crime | 50 | Complete |
| `books/The_Amber_Signal/` | Radio Noir | 50 | Complete |
| `books/The_Crystal_Frontier/` | Planetary Adventure | 50 | Complete |
| `books/The_Mercy_Engine/` | Medical Science Fiction | 50 | Complete |
| `books/The_Paper_Moon_Conspiracy/` | Retro Science Thriller | 50 | Complete |
| `books/The_Glass_Lantern/` | Literary Fiction / Historical Mystery | 50 | Complete |
| `books/The_Fig_Collector/` | Literary Fiction / Travel Narrative / Botanical Fiction | 50 | Complete |
| `books/The_Dyers_Hand/` | Literary Fiction / Historical Fiction / Craft Narrative | 50 | Complete |
| `books/The_Norsewoman/` | Viking Historical Fiction | 50 | Complete |
| `books/The_Pearl_Lagoon/` | Pacific Island Historical Fiction / Colonial Drama | 50 | Complete |
| `books/The_Blue_Ridge_Covenant/` | Appalachian Gothic | 50 | Complete |
| `books/The_Hammam_of_Shadows/` | Ottoman Mystery | 50 | Complete |
| `books/The_Fermentation_Master/` | Korean Literary Fiction / Craft Narrative | 50 | Complete |
| `books/The_Thousand_Faces/` | Psychological Suspense / Clinical Psychology | 50 | Complete |
| `books/The_Glass_Self/` | Psychological Horror / Cotard Delusion | 50 | Complete |
| `books/The_Dark_Mirror/` | Psychological Fiction / NPD | 50 | Complete |
| `books/The_Fragile_Mind/` | Psychological Fiction / DID | 50 | Complete |
| `books/The_Weight_of_Silence/` | Psychological Thriller / Forensic Psychology | 50 | Complete |
| `books/The_Tessera_Bureau/` | Speculative Fiction / Parallel Worlds | 50 | Complete |
| `books/The_House_With_Two_Skies/` | Literary Fiction / Parallel Lives | 50 | Complete |
| `books/The_Color_of_Eight_Thoughts/` | Literary Fiction / Non-Human POV | 50 | Complete |
| `books/The_Understory/` | Literary Fiction / Ecological Non-Human POV | 50 | Complete |
| `books/The_Marginalia/` | Medieval Manuscript Mystery | 50 | Complete |
| `books/The_Moonlit_Apothecary/` | Botanical Gothic Mystery | 50 | Complete |
| `books/The_Sundial_Cipher/` | Renaissance Cryptography Thriller | 50 | Complete |
| `books/The_Ember_Cartographer/` | Volcanic Expedition Adventure | 50 | Complete |

## Git Workflow

- Branch from master for new work.
- Push only when asked.
