#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re

cards = []


def fix(line):
    line = line.strip()
    line = re.sub(r"_+", r"_", line)
    return line


with open("bianche.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    line = fix(line)
    cards.append({
        "text": line,
        "pick": 0,
    })

with open("nere.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    line = fix(line)
    cards.append({
        "text": line.strip(),
        "pick": max(line.count("_"), 1),
    })

with open("cards_ita.json", "w") as f:
    json.dump(cards, f, indent=4)
