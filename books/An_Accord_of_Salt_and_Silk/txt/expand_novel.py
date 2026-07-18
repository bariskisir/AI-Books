import re, os

path = r'C:\Users\white\main\gitrepos\ai-books\books\An_Accord_of_Salt_and_Silk\txt\An_Accord_of_Salt_and_Silk.txt'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Need ~382 more words for 20K

content = content.replace(
    'Marco looked at Elara. "After Florence, we will see."\n\n---\n\n',
    'Marco looked at Elara. "After Florence, we will see."\n\n"There is a city I have heard of," the baker said, leaning forward. "A place called Genoa. They say it rivals Venice for trade."\n\n"Genoa is a rival, not a destination," Elara said. "But perhaps we will see it anyway."\n\nThe table laughed. Wine was poured. Laleh asked for the story of the frozen river, and Marco told it.\n\n---\n\n',
    1
)

content = content.replace(
    'Elara watched from the doorway, a cup of tea warm in her hands.',
    'Elara watched from the doorway, a cup of tea warm in her hands. The house in Florence was smaller than the one in Venice, but it had a garden with an orange tree and a view of the hills. Marco had found work as a factor for a trading company, his knowledge of the eastern routes valuable even in a city that had never seen the Silk Road.\n\nShe did not work. She did not need to. She spent her days in the garden, learning to weave from a woman down the street, teaching Laleh to read and write in Latin and Italian. It was a quiet life. A peaceful life.\n\nShe had never expected to want a quiet life.\n\nMarco found her in the garden one evening. "You look thoughtful."\n\n"I am thinking about the road."\n\n"Do you miss it?"\n\n"I miss the stars. The desert stars were brighter than anything I have ever seen."\n\n"We could go back. Someday."\n\n"Could we?"\n\nHe sat beside her. "The road is still there. It will always be there."\n\nShe leaned against him. The orange tree rustled in the breeze. "I know. That is what makes it bearable to stay."\n\nElara watched from the doorway, a cup of tea warm in her hands.',
    1
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

words = len(content.split())
print(f"Final word count: {words}")
titles = re.findall(r'Chapter \d+: .+', content)
print(f"Chapters: {len(titles)}")
