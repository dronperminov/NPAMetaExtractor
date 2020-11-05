import re
from typing import List, Tuple
from constants import *


class NumberExtractor:
    def __init__(self):
        self.regexps = dict()
        self.regexps[FEDERAL_LAW] = r"\d+-фз"
        self.regexps[DECREE] = r"(?:\d+-у[гн]?|у[пг]-\d+|\d+)"
        self.regexps[RESOLUTION] = r"(?:\d+-п[пгарс]?(?:[/-]\d+)?|\d+а|\d+-\d+-ЗКО|\d+(?:-\d+/\d+)+|\d+/\d+-[ПОС]{0,2}|\d+/\d+|\d+-\d+|\d+-СФ|\d+)"

        self.default_regexp = r"\d+ ?(?:-[а-яА-Я]+|[-/]\d+)*"
        self.divider = r"[\s\S\n]*?№?[\s-]*?"

    def extract_by_regexp(self, regexp: str, text: str, date: str, index: int) -> str:
        numbers = [x.replace(date, "") for x in re.findall(r"^" + date + self.divider + regexp, text, re.M | re.I)]

        if numbers:
            return re.findall(regexp, numbers[index], re.M | re.I)[-1]

        numbers = [x.replace(date, "") for x in re.findall(date + self.divider + regexp, text, re.M | re.I)]

        if numbers:
            return re.findall(regexp, numbers[index], re.M | re.I)[-1]

        return "unknown_number"

    def clear_number(self, number: str, doc_type: str) -> str:
        number = re.sub(r"ПОСТАНОВЛЕНИЕ|ДУМЫ|ЗАКОНОДАТЕЛЬНОЕ", "", number)

        if doc_type == LAW:
            number = re.sub(r"[зЗ]3", "З", number)
            number = re.sub(r"-03", "-ОЗ", number)
            number = re.sub(r"-ТРЗ", "-ЗРТ", number)
        elif doc_type == RESOLUTION:
            if re.fullmatch(r"2\d\d\d(?:-пп)?", number.lower()):
                number = number[1:]

            number = re.sub("ппп", "пп", number.lower())
            number = re.sub(r"-цг", "-пг", number.lower())
            number = re.sub(r"-пц", "-п", number.lower())

        number = number.replace(" ", "")

        return number

    def extract(self, text: str, doc_type: str, date: str) -> str:
        lines = [line for line in text.splitlines() if line]

        for line in lines[::-1]:
            if re.fullmatch(r"[Вв]н\. *№ *" + self.default_regexp, line):
                return self.clear_number(re.findall(self.default_regexp, line)[0], doc_type)

        for line in lines:
            if '%' in line or '|' in line:
                continue

            if re.fullmatch(r"(?:[оО]т *)?" + date + "(?: года)? *№ *" + self.default_regexp, line):
                return self.clear_number(re.findall(self.default_regexp, line)[-1], doc_type)

        for line in lines[-1:-6:-1]:
            if re.fullmatch(r" *№ *" + self.default_regexp, line):
                return self.clear_number(re.findall(self.default_regexp, line)[0], doc_type)

        text = re.sub(r"[Оо] [Зз]аконе", "", text)
        regexp = self.regexps[doc_type] if doc_type in self.regexps else self.default_regexp
        number = self.extract_by_regexp(regexp, text, date, -1 if doc_type in [LAW, FEDERAL_LAW, DISPOSAL] else 0)

        return self.clear_number(number, doc_type)

    # тест точности по каждому из классов
    def test_accuracies(self, data: List[Tuple[str, dict]], predictions: List[dict]):
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}
        correct_all = 0

        for (text, label), prediction in zip(data, predictions):
            if label["number"].lower() == prediction["number"].lower():
                correct[label["type"]] += 1
                correct_all += 1

            total[label["type"]] += 1

        print("Number extractor accuracy test:")
        for doc_type in doc_types:
            print(
                f'{doc_type}: {correct[doc_type]} / {total[doc_type]} ({correct[doc_type] / max(1, total[doc_type])}), incorrect: {total[doc_type] - correct[doc_type]}')

        print(f'Total: {correct_all} / {len(data)} ({correct_all / len(data)})')