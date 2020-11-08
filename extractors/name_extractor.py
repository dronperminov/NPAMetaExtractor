import re
from constants import *
from normalizers.name_normalizer import NameNormalizer
from typing import List, Tuple


class NameExtractor:
    def __init__(self, for_metric=True):
        self.strip_chars = " \n':|-©‚`" + ("\"" if for_metric else "")
        self.name_normalizer = NameNormalizer(self.strip_chars)
        self.paragraph_regexp = re.compile(r"(?:.*\n)+?\n", re.M)

        self.name_regexps = [
            re.compile(r"^О[бБ]? .+$", re.M),
            re.compile(r"^Отдельные .+$", re.M),
            re.compile(r"^Вопросы .+$", re.M),
            re.compile(r"\bО[бБ]? .+$", re.M),
        ]

    def clear_paragraph(self, paragraph: str) -> str:
        return paragraph.strip(self.strip_chars).replace("\n", " ")

    def extract(self, text: str) -> str:
        paragraphs = [self.clear_paragraph(paragraph) for paragraph in self.paragraph_regexp.findall(text + "\n")]

        for i, paragraph in enumerate(paragraphs[:-1]):
            if paragraph.lower().endswith("ого") or paragraph.endswith(","):
                paragraphs[i] += " " + paragraphs[i + 1]
                paragraphs[i + 1] = ""

        text = "\n".join(paragraphs)

        for regexp in self.name_regexps:
            names = regexp.findall(text)

            if names:
                return self.name_normalizer.normalize(names[0])

        return "unknown name"

    # тест точности по каждому из классов
    def test_accuracies(self, data: List[Tuple[str, dict]], predictions: List[dict]):
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}

        correct_all = 0

        for (text, label), prediction in zip(data, predictions):
            if label["name"].lower().replace(" ", "") == prediction["name"].lower().replace(" ", ""):
                correct[label["type"]] += 1
                correct_all += 1

            total[label["type"]] += 1

        print("Name extractor accuracy test:")
        for doc_type in doc_types:
            print(
                f'{doc_type}: {correct[doc_type]} / {total[doc_type]} ({correct[doc_type] / max(1, total[doc_type])}), incorrect: {total[doc_type] - correct[doc_type]}')

        print(f'Total: {correct_all} / {len(data)} ({correct_all / len(data)})')