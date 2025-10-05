from random import choice, randint, random


def os418_curse_apply_silence(text: str):
    r = []
    for ch in text:
        chu = ch.upper()
        if chu == " ":
            chn = " "
        elif chu in EN:
            chn = EN[chu]
        elif chu in RU:
            chn = RU[chu]
        elif chu.isdigit():
            chn = chu
        else:
            chn = choice(OTH)
        if random() < 0.05:
            chn = choice(OTH)
        elif ch != chu:
            chn = chn.lower()
        r.append(chn)
    c = len(r) * 0.15
    while c > 0:
        c -= 1
        r.pop(randint(0, len(r) - 1))

    return "".join(r)


OTH = [".", ",", "=", "+", "-", "_", "*", "#"]

EN = {
    "A": "A",
    "B": "Б",
    "C": "C",
    "D": "D",
    "E": "E",
    "F": "F",
    "G": "Г",
    "H": "Х",
    "I": "И",
    "J": "Ж",
    "K": "K",
    "L": "L",
    "M": "M",
    "N": "N",
    "O": "O",
    "P": "П",
    "Q": "Q",
    "R": "R",
    "S": "S",
    "T": "T",
    "U": "У",
    "V": "V",
    "W": "В",
    "X": "КС",
    "Y": "Й",
    "Z": "З",
}
RU = {
    "А": "А",
    "Б": "Б",
    "В": "В",
    "Г": "Г",
    "Д": "D",
    "Ё": "ЙО",
    "Е": "Е",
    "Ж": "Ж",
    "З": "З",
    "И": "И",
    "Й": "Й",
    "К": "К",
    "Л": "L",
    "М": "М",
    "Н": "N",
    "О": "О",
    "П": "П",
    "Р": "R",
    "С": "S",
    "Т": "Т",
    "У": "У",
    "Ф": "F",
    "Х": "Х",
    "Ц": "Ц",
    "Ч": "Ч",
    "Ш": "Ш",
    "Щ": "Щ",
    "Ъ": "Ъ",
    "Ы": "Ы",
    "Ь": "Ь",
    "Э": "Э",
    "Ю": "ЙУ",
    "Я": "ЙА",
}
