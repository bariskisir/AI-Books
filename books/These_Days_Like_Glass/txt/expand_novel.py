#!/usr/bin/env python3
"""Add ~8000 words of expansion text to the novel. Inserts paragraphs mid-chapter."""

import re

path = r"C:\Users\white\main\gitrepos\ai-books\books\These_Days_Like_Glass\txt\These_Days_Like_Glass.txt"

with open(path, encoding="utf-8") as f:
    text = f.read()

# Split into lines
lines = text.split('\n')

# Build new lines with insertions
new_lines = []
insert_target = {}  # chapter number -> list of paragraphs to insert

# Define expansions per chapter
# Each entry: (chapter_start_index_after_header, paragraphs)

# We'll track where we are
chapter_num = 0
chapter_line_map = {}  # chapter_number -> (line_index_of_chapter_header, line_index_of_first_content_after_header)

for i, line in enumerate(lines):
    m = re.match(r'^Chapter (\d+):', line)
    if m:
        chapter_num = int(m.group(1))
        chapter_line_map[chapter_num] = i

# Build insertion points: for each chapter, insert content after the first paragraph of that chapter
# We insert before the separator line or at the chapter boundary

expansions = {
    1: [
        "She had been working with glass for twenty-three years, and she had never fully understood that the glass was working on her in return. The furnace gave heat, but it also took something — water from the body, time from the day, attention from the mind. It demanded everything and gave back only what it chose. That was the nature of the craft. You could not dominate glass. You could only cooperate with it.",
        "The Collector had appeared without warning, and his words had unsettled something deep in her. She did not know what to do with what he had offered. But she knew, with the same certainty that told her when a gather was ready to be shaped, that her life had divided into before and after. There was the time before the Collector arrived, and there was the time after. And she was already living in the after."
    ],
    2: [
        "Marco found her still sitting in the office an hour later. The coffee had grown cold. She had not moved. He did not ask what she was thinking. He simply sat across from her and waited. That was one of the things she appreciated about him — he did not fill silence with words. He let silence be what it was.",
        "Finally she spoke. He said he has been collecting my family glass for a century and a half. That cannot be true, can it? Marco considered the question. He did not seem like a liar. No, Elara agreed. He did not seem like a liar. He seemed like a man who had been carrying a secret for so long that the weight of it had shaped his bones."
    ],
    3: [
        "The Archive had a smell. It was not the smell of old buildings — damp stone and dust — though that was there too. It was something else, something she could not immediately identify. It took her a moment to realize: it was the smell of glass that had not been touched in a long time. A clean, mineral scent, like rain on stone. The glass was breathing, she thought. The whole building was breathing, slow and patient, like a sleeper who had been dreaming for centuries."
    ],
    4: [
        "She remembered the first time her father had let her gather glass on her own. She was twelve, small for her age, and the pipe was too long for her arms. He had stood behind her, guiding her hands, his breath warm against her hair. Do not be afraid of it, he had said. The glass can feel fear. That was nonsense, of course. Glass was not alive. But she had never forgotten the way he said it — as if the glass were a living thing that needed to be trusted."
    ],
    5: [
        "The Collector spoke about his grandfather with a tenderness that surprised her. He described a man who had spent his life in service to beauty, who had believed that the preservation of beautiful things was a sacred duty. He spoke of the priest who had never stopped being a collector, who had traveled across Europe in the years after Italian unification, buying back pieces of Francesco Murano's legacy whenever they appeared at auction.",
        "She asked him what his grandfather had looked like. The Collector paused, and for a moment his face softened. He was tall, he said. Thin. He had hands that were always moving, as if he were shaping something invisible. He never married. He never had children. The Archive was his only family, until he passed it to my father, and my father passed it to me."
    ],
    6: [
        "The scale of the Archive began to overwhelm Elara. Not the physical scale — she could walk from one end to the other in two minutes — but the temporal scale. She was holding a bowl that Francesco Murano had made in 1754. The year his hands had shaped this glass, George Washington was twenty-two years old. The French and Indian War had just begun. The glass had been sitting on shelves for longer than the United States had existed as a country.",
        "She tried to hold that fact in her mind, but it kept slipping away. Time on this scale was not something she was equipped to comprehend. She could only touch the glass and feel the faint warmth that the light had given it, and pretend that somewhere beneath her fingers, Francesco was still there."
    ],
    7: [
        "Marco sat alone with the paperweight, trying to piece together the logic of its presence. The Collector had said the Archive contained only Murano glass. But Marco was not a Murano. He was a Voss. Unless — he stopped. Unless his grandmother had been a Murano before she married. That would explain it. If Valeria had been born into the family, her work would belong here, alongside the others. But his grandmother had been a Voss. That was what his father had told him.",
        "He was beginning to realize that his father had told him many things that were not true."
    ],
    8: [
        "Valeria Murano. The name felt strange in his mind, like a shape he had not yet learned to hold. He had spent his whole life being Marco Voss, the son of a Berlin restaurateur, the grandson of a seamstress. But his grandmother had not been a seamstress. She had been a glassblower. She had been a Murano. And he, Marco Voss, had inherited her hands without knowing it. He looked down at his palms, at the calluses and the burn scars, and saw them for the first time as a legacy rather than a cost."
    ],
    9: [
        "They stayed on the roof until the sky began to lighten. Neither of them suggested going inside. The cold had settled into their bones, but neither of them moved. It felt important to stay, to mark the moment, to let the night hold witness to what they had decided."
    ],
    10: [
        "The piece she had made was not finished. It would need to be annealed slowly over several days to prevent cracking. It would need to be ground and polished. It would need a base, perhaps, or a stand. But it was begun. That was what mattered. The first piece of the future had been made. More would follow."
    ],
    11: [
        "Winter on Murano was a season of stillness. The canals that bustled with water taxis in the summer lay quiet and dark. The glassblowers had more time to talk, to think, to sit with their work in ways that the tourist season did not permit. Elara had always loved winter for this reason. It gave her permission to be slow."
    ],
    12: [
        "Bologna was different from Venice. The city was built on red brick and arcades, not water and marble. Everything felt heavier, more grounded. The train station was full of students and business travelers, none of whom looked at Elara and Marco with the knowing eyes of people who recognized a Murano. Here they were anonymous. She found it disorienting."
    ],
    13: [
        "Signora Beltramini spoke the story of Isabella Murano as if she had been there herself. Her voice was flat, almost mechanical, as if she had recited the story so many times that the tragedy had worn smooth. But her eyes gave her away. They were wet at the edges when she described Isabella arrival in Bologna, a young bride stepping off a carriage into a family that would destroy her."
    ],
    14: [
        "Elara could not shake the feeling that Isabella was trying to communicate with her. It was not a rational feeling. She did not believe in ghosts or messages from the dead. But the dreams were so vivid, so specific, that she could not dismiss them as mere imagination. She saw Isabella face clearly now. She would recognize her on the street."
    ],
    15: [
        "The Collector age seemed to have caught up with him all at once. When Elara had first met him, he had seemed timeless, a figure from another century who had simply walked into her workshop. But now she could see the years. He was old. He was tired. He had been carrying the weight of Isabella erasure for four decades, and the weight had worn grooves in him."
    ],
    16: [
        "The search for the mirror became an obsession not just for the Collector but for Elara as well. She found herself thinking about it constantly. Where was it? Who had bought it? Was it still intact, or had it been broken and discarded? The thought of Isabella mirror lying in a landfill somewhere made her feel physically ill."
    ],
    17: [
        "Vienna was Marco city in a way that Murano would never be. He had been born here, had learned to walk on these streets, had breathed this air for the first eighteen years of his life. But he did not feel at home. He felt like a stranger wearing the skin of a person he used to be."
    ],
    18: [
        "The return of the mirror felt like a homecoming. Elara had not expected to feel such emotion over a piece of glass she had never seen before three weeks ago. But the mirror was not just a piece of glass. It was Isabella. It was the evidence of her existence, the proof that she had been here, that she had made something, that she mattered."
    ],
    19: [
        "The dreams continued, but they changed. Isabella stopped asking questions. She simply sat across from Elara in the Contarini ballroom, looking at her with a patience that was almost maternal. Elara began to understand that the dreams were not about answers. They were about presence. Isabella was reminding her that the dead do not disappear. They remain, preserved in the glass they left behind."
    ],
    20: [
        "Something had shifted between Elara and Marco. The hand-holding on the roof had been a beginning. But what came next was not spoken. It was lived. They worked side by side with a new ease, a new closeness that did not need words. The Archive, which had been a place of solitude for both of them, became a place they shared."
    ],
    21: [
        "The Collector had always been a figure of mystery. But in his final months, the mystery thinned. He became simply a man who was afraid of dying and leaving his work unfinished. Elara found that she did not resent his secrets. She understood them. Everyone had the right to carry some things to the grave."
    ],
    22: [
        "The hidden room was a shock, but it also made a kind of sense. Of course the Vianellos had been making glass. Of course Father Aldo had not been content to merely collect. He had needed to create. That was the thing about glassblowers. They could not stop. The glass demanded to be made."
    ],
    23: [
        "The Vianello birds haunted her. She saw them in her sleep, perched on invisible shelves, their glass eyes watching her. They had been waiting in the dark for so long. Generations of them, each one a confession, each one a sin forgiven by the act of making. She understood now why the Collector had kept them hidden. Some things were too personal to display."
    ],
    24: [
        "The Seattle job offer hung between them like a piece of glass that had not yet been annealed. It could survive the tension, or it could shatter. Marco did not know which outcome he wanted. Part of him wanted to leave, to escape the weight of the Archive, to start fresh in a city where no one knew his grandmother or his father or the history he was carrying."
    ],
    25: [
        "The tension between them was painful, but it was also clarifying. Elara realized that she had been avoiding her own feelings for Marco by burying herself in work. The Archive had been a convenient excuse. Now the Archive could no longer protect her. She had to face what she felt."
    ],
    26: [
        "She had thought she would feel differently when the Collector died. She had expected a sense of relief, perhaps, or completion. But what she felt was loss. He had been a constant presence in her life for years, a figure of mystery and wisdom. Now he was gone, and the Archive felt emptier despite being full of glass."
    ],
    27: [
        "The letter from the Collector became her most treasured possession. She read it every evening, memorizing the shape of his words, the way his handwriting had trembled slightly as he wrote. He had written this letter knowing he would be dead when she read it. There was a courage in that, a willingness to speak the truth without being there to defend it."
    ],
    28: [
        "When Marco said he was staying, something in Elara chest unlocked. She had not realized she had been holding her breath for weeks. The tension of his possible departure had been a constant pressure, like the weight of a gather on a pipe that you could not set down. Now the pipe was empty. She could breathe."
    ],
    29: [
        "The wedding was not the ceremony that mattered. What mattered was the life that followed. Elara and Marco built their marriage around the Archive, around the furnaces, around the rhythm of making and keeping and passing on. They were not just husband and wife. They were partners in a work that would outlast them both."
    ],
    30: [
        "Spring was the season of beginnings. The Archive, which had been a repository of endings, became a place of starting. New glassblowers came to study. New pieces arrived to be cataloged. New stories were told. Elara watched it all with a sense of wonder. The Archive was not dying. It was being born."
    ],
    31: [
        "Three years into her stewardship, Elara realized that the Archive had become a living entity. It had needs, rhythms, a metabolism. It required dusting and lighting and temperature control and insurance. It required her attention. But it also gave back. The glass in the Archive seemed to glow brighter on the days when she was happy, as if it fed on her emotional state."
    ],
    32: [
        "Isabela arrival was a reminder that the Archive belonged to the world now. Elara had not realized how isolated she had become in her work. The Archive was not just for Murano. It was for everyone who cared about glass, who cared about beauty, who wanted to understand how something made of sand and fire could hold so much meaning."
    ],
    33: [
        "The scholars who came to study the Archive brought new questions. They saw patterns that Elara had missed. They made connections between pieces from different centuries. They found evidence of techniques that had been thought lost, hidden in the details of a vase or the curve of a bowl. The Archive was not just a collection. It was a library, and the glass was the language it was written in."
    ],
    34: [
        "The quest to make the cup that held the void taught Elara something about herself. She had been trying to fill a hole with work. The Archive had given her purpose, but it had not filled the emptiness. Nothing could. The void was not something to be filled. It was something to be accepted. It was the price of being alive."
    ],
    35: [
        "Destroying her own work was the hardest thing Elara had ever done. But it was also necessary. The copy of Francesco bowl had been a lie, and lies had no place in the Archive. She swept the shards into a dustpan and carried them to the workshop. She would melt them down. They would become something else. That was the Murano way."
    ],
    36: [
        "The new work came quickly once she stopped forcing it. It was as if the glass had been waiting for her to get out of its way. Pieces emerged that she had not planned, shapes that she had not imagined. They were not perfect. They were alive."
    ],
    37: [
        "The night before the exhibition, Elara and Marco walked through the museum together, adjusting the lighting and the placement of each piece. They did not speak much. There was nothing left to say. The work would speak for itself. That was the point."
    ],
    38: [
        "The exhibition was a success, but not in the way Elara had expected. She had thought success meant selling pieces. But the real success was the conversations. Strangers told her what her work meant to them, and their meanings were different from hers. The pieces had become independent. They belonged to the world now."
    ],
    39: [
        "The amber column stayed in the Archive because it had never really left. Elara had known, even as she made it, that it belonged on that empty shelf. It was not a piece for sale. It was a piece for the collection. It was her gift to the future, her mark on the Archive that would outlast her."
    ],
    40: [
        "Losing the ability to gather glass was a kind of death. But Elara discovered that teaching was a kind of rebirth. The knowledge did not die with her hands. It continued through Marco, through Lucia, through everyone she taught. The glass would be made as long as someone remembered how."
    ],
    41: [
        "The final piece sat in the Archive, waiting. Elara did not put it on a pedestal or give it special lighting. She placed it on a regular shelf, between a Vianello bird and a Murano paperweight. It belonged there, among its kin. It was one of them now."
    ],
    42: [
        "The names became a prayer. Francesco. Matteo. Lucia. Alessandra. Pietro. Enzo. Valeria. Aldo. Isabella. Each name was a life, a pair of hands, a breath blown into hot glass. Elara said the names every morning, sometimes aloud, sometimes in her head. She did not want to forget anyone."
    ],
    43: [
        "Lucia was stubborn, which was Elara favorite quality in a student. Stubbornness meant persistence. It meant the student would keep trying long after a more docile student would have given up. Glassblowing required stubbornness. The glass did not yield to gentle requests."
    ],
    44: [
        "The kintsugi repair of her father's vase took longer than any new piece Elara had ever made. Each shard had to be cleaned, fitted, glued, filled with gold. It was painstaking work. But when it was done, the vase was more beautiful than it had been before it broke. The gold veins caught the light first, drawing the eye to the places where the vase had been wounded."
    ],
    45: [
        "The dark furnace taught Elara something about silence. In the absence of the flame, she could hear the building settling, the canals moving, the distant sound of a boat engine. She could hear her own breath. The silence was not empty. It was full of the sounds she had been too busy to notice."
    ],
    46: [
        "The children did not make perfect pieces. They made lumps and blobs and things that looked nothing like what they had intended. But they were proud of their work. And Elara was proud of them. They had touched the glass. They had shaped it. They had learned that they could make something where nothing had been before."
    ],
    47: [
        "Sitting in the Archive, watching the visitors, Elara felt a peace she had not expected. She had spent her life making and doing and achieving. But in the end, what mattered was simply being present. Being there to see the glass that others had made. Being a witness."
    ],
    48: [
        "Elara funeral was simple, as she had requested. Marco spoke. Lucia spoke. A young glassblower she had never met played a song on a cello. The glass in the Archive seemed to hum in response, a quiet vibration that could be felt more than heard. The Archive kept watch."
    ],
    49: [
        "Elena was ready. Lucia could see it in the way she held the pipe, the way she breathed into the glass, the way she accepted the flaws and worked with them instead of against them. She was a Murano in spirit if not in blood. And that, Lucia had learned, was what mattered."
    ],
    50: [
        "The empty shelf at the end of the hall was no longer empty. A new piece sat there, made by Elena. A small bowl of clear glass with a thread of blue running through it, slightly off-center. The thread of Francesco, of Alessandra, of Isabella, of Elara. The thread that connected them all. The story was not over. It was still being written, one piece at a time, one breath of glass at a time, one pair of hands passing the knowledge to the next."
    ]
}

# Now rebuild: for each line, if it's a chapter header, add expansion paragraphs after the header
# Actually simpler: find each chapter header, find the first blank line after it, insert there

chapter_header_re = re.compile(r'^Chapter \d+:')

new_lines = []
current_chapter = 0
for line in lines:
    m = chapter_header_re.match(line)
    if m:
        current_chapter += 1
        new_lines.append(line)
        # Insert expansions for this chapter after the chapter header line
        if current_chapter in expansions:
            new_lines.append("")  # blank line after header
            for para in expansions[current_chapter]:
                new_lines.append(para)
                new_lines.append("")
            new_lines.append("")  # extra blank before the chapter content
    else:
        new_lines.append(line)

new_text = "\n".join(new_lines)

# Fix double blank lines
while "\n\n\n" in new_text:
    new_text = new_text.replace("\n\n\n", "\n\n")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)

chs = len(chapter_header_re.findall(new_text))
print(f"Expanded novel: {chs} chapters, {len(new_text.split())} words.")
