import re
from typing import List, Tuple
from constants import *


class TypeExtractor:
    def __init__(self):
        self.main_templates = dict()
        self.main_templates[FEDERAL_LAW] = {"ФЕДЕРАЛЬНЫЙ ЗАКОН"}
        self.main_templates[RESOLUTION] = {"ПОСТАНОВЛЕНИЕ"}
        self.main_templates[ORDER] = {"ПРИКАЗ"}
        self.main_templates[DISPOSAL] = {"РАСПОРЯЖЕНИЕ"}
        self.main_templates[LAW] = {"ЗАКОН", "Закон"}
        self.main_templates[DECREE] = {"УКАЗ"}

        self.lower_templates = dict()
        self.lower_templates[FEDERAL_LAW] = re.compile(r"федеральный закон[ \n]*?о")
        self.lower_templates[RESOLUTION] = re.compile(r"настоящ.*? постановлени.*?|постановление вступает в силу|изменени.*? в постановлени.*| постановляет")
        self.lower_templates[ORDER] = re.compile(r"приказыва.*|приказ вступает в силу")
        self.lower_templates[DISPOSAL] = re.compile(r"распоряжение[ \n]+?президента|настоящее распоряжение\b|\bраспоряжение[ \n]*?от")
        self.lower_templates[LAW] = re.compile(r"настоящ.*? закон.*?|.+?закон вступает в силу")
        self.lower_templates[DECREE] = re.compile(r"настоящ.*? указ.*?|изменени.*? в указ.*|ный указо.+|указ вступает|указ[ \b]*?президента")

    def extract(self, text: str) -> str:
        first_lines = [line for line in text.splitlines() if line][:20]

        for doc_type in doc_types:
            for template in self.main_templates[doc_type]:
                if template in first_lines:
                    return doc_type

        lower = text.lower()

        for doc_type in doc_types:
            if self.lower_templates[doc_type].search(lower):
                return doc_type

        for line in first_lines:
            for doc_type in doc_types:
                for template in self.main_templates[doc_type]:
                    if line.startswith(template) or line.endswith(template):
                        return doc_type

        return RESOLUTION

    # тест точности по каждому из классов
    def test_accuracies(self, data: List[Tuple[str, dict]]):
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}

        correct_all = 0

        for example in data:
            text, answer = example
            doc_type = self.extract(text)

            if answer["type"] == doc_type:
                correct[answer["type"]] += 1
                correct_all += 1

            total[answer["type"]] += 1

        print("Type extractor accuracy test:")
        for doc_type in doc_types:
            print(f'{doc_type}: {correct[doc_type]} / {total[doc_type]} ({correct[doc_type] / total[doc_type]})')

        print(f'Total: {correct_all} / {len(data)} ({correct_all / len(data)})')