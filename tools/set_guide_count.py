"""Set the homepage "travel guides published" count from the guide cards on guides.html (the data calculator is a tool, not a guide)."""
import os
import re
import sys

os.chdir(sys.argv[1])
cards = open("guides.html", encoding="utf-8").read().count('class="guide-card"')
count = cards - 1
t = open("index.html", encoding="utf-8").read()
t2 = re.sub(r'<span class="n">\d+</span><span class="l">travel guides published</span>',
            f'<span class="n">{count}</span><span class="l">travel guides published</span>', t)
if t2 != t:
    open("index.html", "w", encoding="utf-8", newline="\r\n").write(t2)
print("guide count:", count)
