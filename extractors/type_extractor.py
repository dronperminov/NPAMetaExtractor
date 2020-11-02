import re
from typing import List, Tuple
from constants import *


class TypeExtractor:
    def __init__(self):
        self.main_templates = dict()
        self.main_templates[FEDERAL_LAW] = {"ФЕДЕРАЛЬНЫЙ ЗАКОН"}
        self.main_templates[RESOLUTION] = {r"ПОСТАНОВЛЕНИЕ\b(?: +„?\w+)*"}
        self.main_templates[ORDER] = {r"ПРИКАЗ(?: +\w+)?"}
        self.main_templates[DISPOSAL] = {r"РАСПОРЯЖЕНИЕ(?: +\w+)*\W?"}
        self.main_templates[LAW] = {r"ЗАКОН\b(?: +\w+)*", r"Закон\b(?: +\w+)*"}
        self.main_templates[DECREE] = {"УКАЗ", r"\d+-[уУ]"}

        self.lower_templates = dict()
        self.lower_templates[FEDERAL_LAW] = re.compile(r"настоящ.*? федеральный закон")
        self.lower_templates[RESOLUTION] = re.compile(r"настоящ.\w*? постановлени.*?|постановление вступает в силу|изменени\w*? в.*? постановлени.*|(?:правительство|совет).*?постановляет:|утвержденное[ \n]*постановлением")
        self.lower_templates[ORDER] = re.compile(r"приказы ?ва.*|приказ вступает в силу|настоящ.*? приказ|утратившим силу приказ")
        self.lower_templates[DISPOSAL] = re.compile(r"распоряжение[ \n]+?президента|настоящ\w*? распоряжен.*?\b|\bраспоряжение[ \n]*?от|\bизменени\w в распоряжени")
        self.lower_templates[LAW] = re.compile(r"настоящ\w*? закон.*?|.+?закон вступает в силу|\nо внесении изменени\w в (?:статью \d+ )?закон")
        self.lower_templates[DECREE] = re.compile(r"настоящ\w*? указ.*?|изменени\w*? в указ.*|ный указо.+|указ вступает|указ[ \b]*?президента|опубликовать указ|утверждены\nуказом|названным указом|^о награждении", re.M)

    def extract(self, text: str) -> str:
        lines = [line for line in text.splitlines() if line]
        first_lines = lines[:15]
        last_lines = lines[-40:]

        for line in last_lines[::-1]:
            if re.search(r"^(?:\d+\. )?Настоящий [зЗ]акон вступает в силу", line):
                return LAW

        for doc_type in doc_types:
            for template in self.main_templates[doc_type]:
                for line in first_lines:
                    if re.fullmatch(template, line):
                        return doc_type

        lower = text.lower()

        for doc_type in doc_types:
            if self.lower_templates[doc_type].search(lower):
                return doc_type

        for line in lines:
            for doc_type in doc_types:
                for template in self.main_templates[doc_type]:
                    if re.search(r"^" + template, line) or re.search(template + r"$", line):
                        return doc_type

        if re.search(r"\bпостановля(?:ет|ю):", lower):
            return RESOLUTION

        return ORDER

    # тест точности по каждому из классов
    def test_accuracies(self, data: List[Tuple[str, dict]], predictions: List[dict]):
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}

        correct_all = 0

        for (text, label), prediction in zip(data, predictions):
            if label["type"] == prediction["type"]:
                correct[label["type"]] += 1
                correct_all += 1

            total[label["type"]] += 1

        print("Type extractor accuracy test:")
        for doc_type in doc_types:
            print(f'{doc_type}: {correct[doc_type]} / {total[doc_type]} ({correct[doc_type] / total[doc_type]})')

        print(f'Total: {correct_all} / {len(data)} ({correct_all / len(data)})')
