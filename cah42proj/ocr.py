#!/usr/bin/python3

import sys
from pathlib import Path

import pdf2image
import pytesseract
from PIL import Image, ImageOps


def read_pages(path, short_name, pages, crop):
    cx = 4
    cy = 5
    with open("cards.txt", "a+") as f:
        for p, img in enumerate(pages):
            img = img.crop(crop)
            w = img.width / cx
            h = img.height / cy
            for y in range(cy):
                for x in range(cx):
                    card = img.crop([w * x, h * y, w * x + w, h * y + h])
                    is_black = sum(img.resize([1, 1], Image.BILINEAR).getpixel((0, 0))) / 3 < 128
                    if is_black:
                        card = ImageOps.invert(card)
                    text = pytesseract.image_to_string(card, lang="ita").strip().replace("\n", " ")
                    text = "{s}.{p}[{x}]x[{y}]_{b}:\t{t}\n".format(s=short_name, p=p, x=x, y=y, b=("b" if is_black else "w"), t=text)
                    f.write(text)
                    print(text)


path = "[CaH42Proj]_Gioco_Stampabile_Copia_Numero_137600.pdf"
pages = pdf2image.convert_from_path(path)[1:44]
read_pages(path, "g", pages, [82, 69, 1631, 2004])

path = "[CaH42Proj]_1Expansion_Copia_Numero_49591.pdf"
pages = pdf2image.convert_from_path(path)[2:]
read_pages(path, "1e", pages, [87, 71, 1634, 2005])

path = "[CaH42Proj]_1.5Expansion_by_Pippi-e-Cecca_Copia_Numero_18294.pdf"
pages = pdf2image.convert_from_path(path)[8:]
read_pages(path, "1_5e", pages, [54, 106, 1646, 2095])
