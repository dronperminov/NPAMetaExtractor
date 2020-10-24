import re


class TesseractNormalizer:
    def __init__(self):
        self.trash_chars = " !#$%&'*+,-/:;<=>?@[\\]^_`{|}©®°і‘’‚…‹›№"
        self.rules = [
            (re.compile(r"\b[пПН]?ОС[Г]?ТА[НВ][О.]В[ЛП]ЕНИ[ЕК]{1,2}\b"), "ПОСТАНОВЛЕНИЕ"),
            (re.compile(r"\b[ПН]{1,2} ?Р ?И ?К ?А ?З\b"), "ПРИКАЗ"),
            (re.compile(r"\bУ ?К ?А ?З\b"), "УКАЗ"),

            (re.compile(r"\bд?ека[бо]ря", re.I), "декабря"),
            (re.compile(r"ИиЮюНня", re.I), "июня"),
            (re.compile(r"от О"), "от ")
        ]

    def normalize(self, text: str) -> str:
        lines = [line.strip(self.trash_chars) for line in text.splitlines()]
        lines = [line for line in lines if line]
        text = "\n".join(lines)
        text = text.replace("_", " ")

        for regexp, replacement in self.rules:
            text = regexp.sub(replacement, text)

        for match in re.finditer(r"[о0О][тТ]\d", text):
            start, end = match.span()
            text = text[:start] + 'от ' + text[end - 1:]

        return text
