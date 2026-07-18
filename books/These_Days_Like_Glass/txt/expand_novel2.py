#!/usr/bin/env python3
"""Add more expansion content to reach ~20K words."""

import re

path = r"C:\Users\white\main\gitrepos\ai-books\books\These_Days_Like_Glass\txt\These_Days_Like_Glass.txt"

with open(path, encoding="utf-8") as f:
    text = f.read()

lines = text.split('\n')

# Additional expansions - more text per chapter
more_text = {
    1: [
        "The furnace was the heart of the workshop. Without it, nothing could be made. Elara had learned this lesson early, as a child watching her father light the burners at dawn. The fire had to be fed, tended, respected. It was not a tool. It was a partner. She thought about this as she stood in the gallery, looking at the space where the Collector had stood. He had walked into her life and changed everything in the span of ten minutes.",
        "The glass rose sat on the cooling rack, its petals catching the light. She would not sell it. She would keep it, a reminder of the day she had stopped fighting the glass. The Collector had appeared on that same day, as if the rose had summoned him. Perhaps it had."
    ],
    5: [
        "The blue thread in Francesco's bowl was the color of the sky over the lagoon in late autumn. Elara had seen that color a thousand times without really seeing it. Now she saw it everywhere. In the canal water. In the glass of windows. In the eyes of the Collector. It was a color that carried memory, that held the light of a specific season in a specific place. Francesco had captured it by accident, and the accident had become the family's signature."
    ],
    8: [
        "Marco looked at the paperweight and saw his entire life refracted through its colors. The blue was Berlin, the gray mornings, the rain on cobblestones. The green was the park near his childhood home, the grass where he had played, the leaves of the trees that lined the street. The red was his grandmother's thread, the connection to Murano that he had carried without knowing it. All of it was there, trapped in glass. All of it was him."
    ],
    10: [
        "The piece she had made was not a masterpiece. But it was a beginning. And beginnings, she had learned, were more important than masterpieces. Without a beginning, there could be nothing else. The first piece of the future sat on the cooling rack, still warm, and she looked at it with the same wonder she had felt as a child when she first saw glass take shape. The wonder had never left her. It had only been waiting."
    ],
    11: [
        "The ledgers told stories that the glass could not. They recorded prices paid and received, the names of merchants and collectors, the dates of shipments and deliveries. But they also recorded things that had no place in a formal account book: the birth of a child, the death of a parent, the illness that had kept a glassblower from the furnace for a month. These marginal notes were the most precious part of the Archive, because they reminded Elara that her ancestors had been people, not just names on plaques."
    ],
    12: [
        "The housekeeper led them through rooms that had not been cleaned in decades. Dust covered every surface. The furniture was draped in white sheets that had yellowed with age. The air was cold and still. It felt like walking through a tomb. And at the center of it all, the chandelier hung like a frozen flame, its glass leaves and flowers catching what little light there was and holding it."
    ],
    14: [
        "The death certificate was a cold document, legal and impersonal. But the words on it had the weight of a verdict. Avvelenamento. Poison. Someone had killed Isabella Murano. Someone had decided that she should not live. And then her family had erased her from the Archive, as if she had never existed. Elara could not undo what had been done to Isabella. But she could make sure that Isabella was remembered."
    ],
    18: [
        "The Collector wept when he saw the mirror. Elara had never seen him weep before. She looked away, giving him privacy. He had spent forty years trying to undo a mistake he had made as a young man. Now the mistake was undone. The mirror was home. And Isabella, at last, had been returned to her family."
    ],
    20: [
        "The Archive was not a monument to death. It was a celebration of life. Every piece in it was evidence that someone had lived, had worked, had made something beautiful. Elara touched the pieces as she walked — the cool surface of a vase, the smooth curve of a bowl — and felt the presence of the hands that had shaped them. The dead were not gone. They were here, in the glass."
    ],
    24: [
        "Elara realized that she had been afraid of losing Marco for longer than she had allowed herself to admit. The fear had been there from the beginning, a shadow at the edge of her awareness. She had pushed it away, buried it in work. But now it was demanding to be felt. She sat alone in the Archive after Marco left the hidden room, and she let herself feel it. The fear was sharp and cold. But it was also clarifying. It told her what she wanted."
    ],
    28: [
        "The decision not to leave was the most important decision Marco had ever made. He knew this. He had come to Murano running away from something. Now he was choosing to stay, to build, to commit. It felt different. It felt like becoming an adult. He looked at Elara across the furnace room, the heat of the flame between them, and he knew that he was exactly where he was supposed to be."
    ],
    30: [
        "Elara watched the Vianello birds in their new gallery. They were no longer hidden. They were displayed in the light, their colors visible, their beauty accessible to anyone who came to see them. She thought about Father Aldo, who had made these birds in secret, who had never shown them to anyone. She wished he could see them now. She wished he could know that his work had finally been seen."
    ],
    33: [
        "The thesis written by the Cambridge student analyzed the relationship between the Murano and Vianello collections. It argued that the two families had developed in parallel, each influencing the other without knowing it. The Vianellos had learned from watching the Muranos. The Muranos had absorbed Vianello techniques through the indirect channel of the market. They were two strands of the same tradition, separated by a secret that had lasted two centuries."
    ],
    35: [
        "The sound of glass breaking was one of the worst sounds in the world. It was sharp and final and irreversible. Elara had heard it many times in her career, every time a piece fell or cracked or shattered in the annealing. But hearing it when she was the one who had done the breaking was different. She had chosen to destroy her own work. And in that destruction, she had found something like freedom."
    ],
    38: [
        "The old woman who spoke to her about the cracked bell had tears in her eyes. She did not explain why the bell moved her. She did not have to. Elara understood that the piece had touched something in her, some memory or loss or hope that words could not reach. That was what glass could do, at its best. It could speak without language. It could reach into the places where words could not go."
    ],
    41: [
        "Elara last piece was not her best work. It was simple, almost plain. But it was true. She had made it without pretense, without trying to impress or prove anything. She had made it the way Francesco had made his first bowl, with nothing but the desire to shape something honest. It sat on its shelf, unremarkable, perfect."
    ],
    43: [
        "Lucia understood, finally, what Elara had been trying to teach her. The flaw was not a mistake. It was a signature. The blue thread that ran off-center was not a failure of skill. It was a declaration of humanity. No machine could have made that thread run off-center with such deliberate imperfection. Only a human hand could do that. Only a human heart would choose to."
    ],
    46: [
        "The glass fish sat on its shelf beside Francesco green bottle. Two pieces of glass, made by children two and a half centuries apart. They had nothing in common except the fact that they had been made by young hands learning the weight and heat and possibility of glass. Elara looked at them every morning. They reminded her that the Archive was not just for masters. It was for everyone who had ever tried."
    ],
    50: [
        "The story of the Murano family was not a story about glass. It was a story about people who refused to stop making. They made through war and peace, through poverty and wealth, through grief and joy. They made because making was what they did, what they were, what they had always been. The glass was just the evidence. The real thing was the making itself.",
        "Elena touched the blue thread in her bowl. It was slightly off-center. She had not intended that. But she had not corrected it either. The flaw was hers. The imperfection was hers. She had made something true."
    ]
}

# Insert more_text after chapter headers
chapter_header_re = re.compile(r'^Chapter \d+:')

new_lines = []
current_chapter = 0
for line in lines:
    m = chapter_header_re.match(line)
    if m:
        current_chapter += 1
        new_lines.append(line)
        new_lines.append("")
        if current_chapter in more_text:
            for para in more_text[current_chapter]:
                new_lines.append(para)
                new_lines.append("")
    else:
        new_lines.append(line)

new_text = "\n".join(new_lines)

while "\n\n\n" in new_text:
    new_text = new_text.replace("\n\n\n", "\n\n")

# Fix leading blank lines in chapters
while "\n\n---" in new_text:
    new_text = new_text.replace("\n\n---", "\n---")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)

chs = len(chapter_header_re.findall(new_text))
print(f"Final novel: {chs} chapters, {len(new_text.split())} words.")
