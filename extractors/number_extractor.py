import re
from constants import *
from normalizers.number_normalizer import NumberNormalizer


class NumberExtractor:
    def __init__(self):
        self.regexps = dict()
        self.regexps[FEDERAL_LAW] = r"\d+-фз"
        self.regexps[DECREE] = r"(?:\d+-у[гн]?|у[пг]-\d+|\d+)"
        self.regexps[RESOLUTION] = r"(?:\d+-п[пгарс]?(?:[/-]\d+)?|\d+а|\d+-\d+-ЗКО|\d+(?:-\d+/\d+)+|\d+/\d+-[ПОС]{0,2}|\d+/\d+|\d+-\d+|\d+-СФ|\d+)"
        self.regexps[ORDER] = r"\d+ ?(?:-?[а-яА-Я]+|[-/]\d+)*"

        self.default_regexp = r"\d+ ?(?:-[а-яА-Я]+|[-/]\d+)*"
        self.divider = r"[\s\S\n]*?№?[\s-]*?"
        self.number_normalizer = NumberNormalizer()

    def extract_by_regexp(self, regexp: str, text: str, date: str, index: int) -> str:
        numbers = re.findall(date + self.divider + "(" + regexp + ")", text, re.M | re.I)

        if numbers:
            return numbers[index]

        return "unknown_number"

    def extract(self, text: str, doc_type: str, date: str) -> str:
        text = re.sub("—", "-", text)
        lines = [line for line in text.splitlines() if len(line) > 2]

        for line in lines[::-1]:
            if re.fullmatch(r"[Вв]н\. *№ *" + self.default_regexp, line):
                return self.number_normalizer.normalize(re.findall(self.default_regexp, line)[0], doc_type)

            numbers = re.findall(r"(?:.*\\)+(" + self.default_regexp + r")\.Йосх", line)

            if numbers:
                return numbers[-1]

        if doc_type == LAW:
            for line in lines[-1:-6:-1]:
                if re.fullmatch(r" *№ *" + self.default_regexp + r"(?: года| г\.)?", line):
                    return self.number_normalizer.normalize(re.findall(self.default_regexp, line)[0], doc_type)

        for line in lines:
            if '%' in line or '|' in line:
                continue

            if re.fullmatch(r"(?:[оО]т *)?" + date + ".*[№ж®] *" + self.default_regexp, line):
                return self.number_normalizer.normalize(re.findall(self.default_regexp, line)[-1], doc_type)

        for line in lines[-1:-6:-1]:
            if re.fullmatch(r" *№ *" + self.default_regexp + r"(?: года| г\.)?", line):
                return self.number_normalizer.normalize(re.findall(self.default_regexp, line)[0], doc_type)

        text = re.sub(r"[Оо] [Зз]аконе", "", text)
        regexp = self.regexps[doc_type] if doc_type in self.regexps else self.default_regexp
        number = self.extract_by_regexp(regexp, text, date, -1 if doc_type in [LAW, FEDERAL_LAW, DISPOSAL] else 0)

        return self.number_normalizer.normalize(number, doc_type)
