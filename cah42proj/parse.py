import re

with open("cards.txt", "r") as f:
    cards = f.read().split("\n")

rc = re.compile(r"^(.*?)\.([0-9]*)\[([0-9]*)\]x\[([0-9]*)\]_(.):\t(.*)$")
with open("parsed_cards.txt", "w+") as f:
    for card in cards:
        m = rc.match(card)
        if m is None:
            print(card)
            quit()
        card = {
            "file": m.group(1),
            "page": m.group(2),
            "x": m.group(3),
            "y": m.group(4),
            "type": m.group(5),
            "text": m.group(6),
        }
        text = card["text"]
        text = re.sub(r"^(.*[.?!])\s{2,}.*$", r"\1", text, flags=re.IGNORECASE)
        text = re.sub(r"^(.*)\s{2,}.*?C?ards Against Humanit?y.*$", r"\1", text, flags=re.IGNORECASE)
        text = re.sub(r"^(.*)\s{2,}.*EXPANSION 1.*$", r"\1", text, flags=re.IGNORECASE)
        print(text)
        # quit()
