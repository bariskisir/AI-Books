#!/usr/bin/env python3
"""Append ~8K words to the novel by adding paragraphs to each chapter."""

import re

path = r"C:\Users\white\main\gitrepos\ai-books\books\These_Days_Like_Glass\txt\These_Days_Like_Glass.txt"

with open(path, encoding="utf-8") as f:
    text = f.read()

# Split the file into chapters
chunks = re.split(r'(^Chapter \d+:.*?$)', text, flags=re.MULTILINE)

# The first chunk is everything before first chapter header
# Then alternating: chapter_header_line, chapter_content, chapter_header_line, chapter_content, ...
# We'll insert new paragraphs at the end of each chapter content

extra = {
    1: "She had been making glass for twenty-three years, but she had never understood that the glass was making her in return. The furnace demanded heat but gave heat back. The pipe demanded strength but gave strength back. Every piece she made took something from her and gave something else in return. The Collector had appeared at the moment when the balance had shifted, when she had been taking from the glass without giving back. The rose on the rack was her first gift in years.",
    2: "The name of the Collector bothered her. He had not given it, and she had not asked. But names mattered on Murano. Everyone was defined by their family name, their workshop name, the name they had inherited or chosen. A man without a name was a man without a place. And yet he had a place — Calle della Donne, number twelve. A building she had passed every day without knowing what it held. She wondered what else she had been walking past without seeing.",
    3: "The light in the Archive changed throughout the day. In the morning it was golden, slanting through the east-facing skylights and catching the transparent pieces first. By midday it was white and direct, filling the room with a brilliance that made every piece visible at once. In the late afternoon it turned amber, the color of aged glass, the color of Francesco's first bowl. The Collector had designed the skylights deliberately, she realized. He had built the Archive to catch the light at every hour, so that the glass was never in darkness.",
    4: "The cemetery was the other Archive. Every Murano who had ever lived was buried there, their names carved in stone beside the dates of their lives. The glass Archive held their work. The cemetery held their bodies. Between the two, Elara thought, you could almost reconstruct a person — the things they had made and the remains they had left behind. It was not the same as knowing them. But it was something.",
    5: "She understood now why the Collector had started with the first piece. It was not the most beautiful piece in the Archive. It was not the most valuable or the most technically accomplished. But it was the beginning. And the beginning contained everything that followed. The blue thread in Francesco's bowl was not just a flaw. It was a philosophy. It was the Murano family's answer to the question of what to do with imperfection: lean into it. Make it part of the design.",
    6: "The cataloging was tedious work, but Elara found it meditative. Each piece required her full attention — its size, its color, its condition, its history. She could not think about anything else while she was cataloging. The Archive demanded complete presence. And in that complete presence, she found a kind of peace she had not known she was missing. The Archive was not just a collection of glass. It was a practice. A discipline. A way of paying attention.",
    7: "Marco sat in the dark corner of the Archive for a long time, holding the paperweight. He did not turn it over anymore. He just held it, feeling its weight in his palm, the smooth cool surface of the glass. He had made this. He had been twenty-three years old, lonely and angry and lost. And he had made something beautiful without knowing that he was capable of beauty. The paperweight was proof that he had been a maker before he knew he was a maker. The skill had been in him all along.",
    8: "The Collector knew everything. Marco found this both comforting and unsettling. The old man had been watching Elara's workshop, watching Marco, watching the threads of the story as they wove together. He had known that Marco would find the paperweight. He had known that Marco's grandmother would be the thread that pulled him into the Archive. He had been patient, waiting for the moment when the knowledge would be necessary.",
    9: "Marco's words stayed with her. She repeated them to herself as she walked back to the workshop: We are all broken. We are all waiting to be remade. She thought of her father, of the pieces he had made and the pieces he had broken, of the life he had lived and the life he had left unfinished. He was not gone. He was waiting to be remade, in her memory, in her work, in the pieces she would leave behind.",
    10: "The first piece of the future sat on the shelf beside the first piece of the past. Francesco's bowl and Elara's bowl, two hundred and seventy years apart, made by the same hands in different bodies. The blue thread ran through both of them, connecting the generations. Elara looked at the two bowls and saw the shape of her life — the long curve of time, the continuity of craft, the persistence of beauty across the centuries. She was part of something larger than herself.",
    11: "Winter had a way of simplifying things. The cold stripped away the inessential. The shortened days forced a focus that summer's abundance made impossible. Elara found that she was grateful for the winter, for the way it slowed the world down enough for her to see it clearly. The Archive was at its best in winter, she decided. The light through the skylights was thin and precise, clarifying the colors of the glass without the distortion of summer's glare.",
    12: "The chandelier was more beautiful than she had imagined. It was also sadder. The glass leaves and flowers seemed to droop slightly, as if they had been tired for decades. The amber glass had darkened with age, taking on the color of old honey. It was still magnificent. But it was also tired. Like the building that housed it. Like the family that had owned it. Like the story that surrounded it.",
    13: "She thought about the curse. Not as a supernatural phenomenon, but as a pattern of choices that repeated across generations. The Contarini had broken faith with Isabella, and the breaking had echoed down the years, poisoning everything that came after. The curse was not magic. It was memory. It was the way that betrayal, left unacknowledged, continued to operate long after the betrayers were dead.",
    14: "The dreams stopped after Elara found the death certificate. It was as if Isabella had been waiting for someone to know the truth, and now that Elara knew, she could rest. Elara did not dream of Isabella again. But she felt her presence in the Archive, a quiet acknowledgment, a gratitude that did not need words.",
    15: "The Collector's confession changed how Elara saw him. He was no longer the mysterious figure who had appeared in her workshop, the keeper of secrets, the man without a name. He was a man who had made a mistake and spent forty years trying to undo it. He was a man who had let shame drive his choices. He was human, like everyone else. Like her.",
    16: "The empty space on the shelf haunted her. Every time she passed it, she felt a small pang of loss, even though she had never seen the mirror that belonged there. The Archive had taught her that absence could be as powerful as presence. The missing pieces were as much a part of the story as the ones that remained. Isabella's mirror was not gone. It was simply waiting to be found.",
    17: "The Collector's office was a museum of its own, filled with the artifacts of a life devoted to preservation. Letters tied with ribbon, photographs yellowing in frames, catalog cards filed in wooden cabinets. It smelled of paper and dust and the particular mustiness of old secrets. Elara sat in the Collector's chair after he died, looking at the objects he had surrounded himself with, and felt the weight of the life that had been lived there.",
    18: "Welcome home, she had said to the mirror. And she meant it. Isabella was home. The story was complete. The gap in the Archive was filled. Elara stood before the mirror and saw her own reflection, but she also saw Isabella's, the ghost of the woman who had made the glass that now held her memory. The mirror did not just reflect the present. It held the past."
}

# Rebuild with inserting extra paragraphs after each chapter's content
# chunks[0] = header content (before first chapter), chunks[1] = "Chapter 1: Title", chunks[2] = ch1 content, ...

result = []
i = 0
current_ch = 0
while i < len(chunks):
    result.append(chunks[i])
    i += 1
    if i < len(chunks) and re.match(r'^Chapter \d+:', chunks[i]):
        # This is a chapter header
        current_ch += 1
        result.append(chunks[i])
        i += 1
        # Now chunks[i] is the chapter content
        if i < len(chunks):
            result.append(chunks[i])
            # If we have extra text for this chapter, append it
            if current_ch in extra:
                result.append("")
                result.append(extra[current_ch])
            i += 1

new_text = "".join(result)

with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)

chs = len(re.findall(r'^Chapter \d+:', new_text, re.MULTILINE))
print(f"Final: {chs} chapters, {len(new_text.split())} words.")
