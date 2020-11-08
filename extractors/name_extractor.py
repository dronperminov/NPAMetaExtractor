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
