import re


class TesseractNormalizer:
    def __init__(self):
        self.trash_chars = " !#$%&'*+,-/:;<=>?@[\\]^_`{|}©®°і‘’‚…‹›№"
        self.rules = [
            (re.compile(r"\b[пПН]?ОС[Г]?ТА[НВ][О.]В[ЛП]ЕНИ[ЕК]{1,2}\b"), "ПОСТАНОВЛЕНИЕ"),
            (re.compile(r"\b[ПН]{1,2} ?Р ?И ?К ?А ?З\b"), "ПРИКАЗ"),
            (re.compile(r"\bУ ?К ?А ?З\b"), "УКАЗ")
        ]

    def normalize(self, text: str) -> str:
        lines = [line.strip(self.trash_chars) for line in text.splitlines()]
        lines = [line for line in lines if line]
        text = "\n".join(lines)

        for regexp, replacement in self.rules:
            text = regexp.sub(replacement, text)

        return text
