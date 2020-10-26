import re


class TesseractNormalizer:
    def __init__(self):
        self.trash_chars = " !#$%&'*+,-/:;<=>?@[\\]^_`{|}©®°і‘’‚…‹›"
        self.rules = [
            (re.compile(r"\b[пПН]?ОС[Г]?ТА[НВ][О.]В[ЛП]ЕНИ[ЕК]{0,3}\b"), "ПОСТАНОВЛЕНИЕ"),
            (re.compile(r"\b[ПН]{1,2} ?Р ?И ?К ?А ?З\b"), "ПРИКАЗ"),
            (re.compile(r"\bУ ?К ?А ?З\b"), "УКАЗ"),

            (re.compile(r"\bд?ека[бо]ря|\bдекабряо", re.I), "декабря"),
            (re.compile(r"ИиЮюНня", re.I), "июня"),
            (re.compile(r"\"ЯНВ&Ё‚Я", re.I), "января"),
            (re.compile(r"оК\*ЪЯбря", re.I), "октября"),
            (re.compile(r"от О"), "от "),
            (re.compile(r"2ипецк", re.I), "Липецк"),
            (re.compile(r"-п0|-п П", re.I), "-пп"),
            (re.compile(r"[еЕ]7"), "17"),
            (re.compile(r"1\]"), "п"),
            (re.compile(r"отмепне", re.I), "отмене"),
            (re.compile(r"`"), ""),
            (re.compile(r"Гукуй-Мектеб"), "Тукуй-Мектеб"),
            (re.compile(r"}"), ")"),
            (re.compile(r"{"), "("),
            (re.compile(r"Ёакон"), "Закон"),
            (re.compile(r"ситуациий"), "ситуаций"),
            (re.compile(r"КЕдиной"), "Единой"),
            (re.compile(r"скои"), "ской"),
            (re.compile(r"СКОЙ"), "СКОЙ"),
            (re.compile(r"НЕНЕ[ЦК]*О?ГО", re.I), "НЕНЕЦКОГО"),
            (re.compile(r"ЛВТОНОМНОГО", re.I), "АВТОНОМНОГО"),
            (re.compile(r"Ъ/\["), "М"),
            (re.compile(r"ульяёбёскои"), "ульяновской")
        ]

    def normalize(self, text: str, strip_lines=True) -> str:
        for regexp, replacement in self.rules:
            text = regexp.sub(replacement, text)

        if not strip_lines:
            return text

        lines = [line.strip(self.trash_chars) for line in text.splitlines()]
        text = "\n".join(lines)

        text = re.sub(r"[_}{#‘]", " ", text)

        matches = [match for match in re.finditer(r"[о0О][тТ]\d", text)]
        for match in matches[::-1]:
            start, end = match.span()
            text = text[:start] + 'от ' + text[end - 1:]

        matches = [match for match in re.finditer(r"\"\d+\"", text)]
        for match in matches[::-1]:
            start, end = match.span()
            text = text[:start] + text[start+1:end] + text[end+1:]

        matches = [match for match in re.finditer(r"[12][09]\d\dг", text)]
        for match in matches[::-1]:
            start, end = match.span()
            text = text[:start+4] + ' г' + text[end:]

        return text
