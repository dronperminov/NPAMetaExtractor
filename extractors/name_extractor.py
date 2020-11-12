import re
from normalizers.name_normalizer import NameNormalizer


class NameExtractor:
    def __init__(self, for_metric=True):
        self.strip_chars = " \n':|-©‚`"
        self.lstrip_chars = "-"
        self.name_normalizer = NameNormalizer(self.strip_chars + ("\"" if for_metric else ""))
        self.paragraph_regexp = re.compile(r"(?:.*\n)+?\n", re.M)

        self.name_regexps = [
            re.compile(r"^Г?О[бБ]? .+$", re.M),
            re.compile(r"^Отдельные .+$", re.M),
            re.compile(r"^Вопросы .+$", re.M),
            re.compile(r"по делу о.*$", re.M),
            re.compile(r"\bО[бБ]? .+$", re.M),
        ]

    def clear_paragraph(self, paragraph: str) -> str:
        lines = [line.lstrip(self.lstrip_chars) for line in paragraph.splitlines() if not re.fullmatch(r"О(?: \d+)*", line)]
        paragraph = "\n".join(lines)

        return paragraph.strip(self.strip_chars).replace("\n", " ")

    def can_join_paragraphs(self, paragraph1: str, paragraph2: str) -> bool:
        if paragraph1.lower().endswith("ого") or paragraph1.endswith(","):
            return True

        if re.search(r"^(?:на |в |об? |\"Об? |Республики )", paragraph2):
            return True

        return False

    def extract(self, text: str) -> str:
        paragraphs = [self.clear_paragraph(paragraph) for paragraph in self.paragraph_regexp.findall(text + "\n")]

        for i, paragraph in enumerate(paragraphs[:-1]):
            if self.can_join_paragraphs(paragraph, paragraphs[i + 1]):
                paragraphs[i] += " " + paragraphs[i + 1]
                paragraphs[i + 1] = ""

        text = "\n".join(paragraphs)

        for regexp in self.name_regexps:
            names = regexp.findall(text)

            if names:
                return self.name_normalizer.normalize(names[0])

        return "unknown name"
