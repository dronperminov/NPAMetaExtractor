import re
from constants import *


class AuthorityExtractor:
    def __init__(self, for_metric=True):
        self.strip_chars = " \n':|-.,‘’°©^" + ("\"" if for_metric else "")

        self.date_regexps = [
            re.compile(r"[0-3оО]?[\dоО].? *?[а-яА-Я][а-яА-Я]+[\n\- ]*[12][09]\d\d(?: ?года)?"),
            re.compile(r"[0-3оО]?[\dоО][./, ][01о]?[\dоО][./, ] ?[12][09]\d\d(?: ?года)?")
        ]

    def clear_authority(self, authority: str) -> str:
        for date_regexp in self.date_regexps:
            authority = date_regexp.sub("", authority)

        authority = authority.replace("'", "\"")
        authority = re.sub("[|=*]", "", authority)
        authority = authority.replace("_", " ")
        authority = authority.strip(self.strip_chars)

        authority = re.sub("губернатора", "губернатор", authority.lower())
        authority = re.sub("администрации", "администрация", authority.lower())
        authority = re.sub("главы", "глава", authority.lower())
        authority = re.sub("совета|советом", "совет", authority.lower())
        authority = re.sub("президента|президентом", "президент", authority.lower())
        authority = re.sub("государственным", "государственный", authority.lower())
        authority = re.sub("думой", "дума", authority.lower())
        authority = re.sub("законодательным", "законодательное", authority.lower())
        authority = re.sub("законодательной", "законодательная", authority.lower())
        authority = re.sub("собранием", "собрание", authority.lower())
        authority = re.sub("областной д", "областная д", authority.lower())
        authority = re.sub("ской областная", "ская областная", authority.lower())

        while "  " in authority:
            authority = authority.replace("  ", " ")

        if authority.endswith(" ."):
            authority = authority[:-2]

        match = re.search(r"\w+ созыва", authority)

        if match:
            start, end = match.span()
            authority = authority[:start]

        return authority

    def __clear_paragraph(self, paragraph: str) -> str:
        lines = paragraph.splitlines()

        for i, line in enumerate(lines):
            if len(line) < 5:
                line = ""

            lines[i] = re.sub("ФЕДЕРАЛЬНЫЙ ЗАКОН|У ?К ?А ?З|[ПН]{1,2} ?Р ?И ?К ?А ?З|ЗАКОН$", "", line)

        return " ".join([line for line in lines if line]).strip()

    def extract_federal_law(self) -> str:
        return "Государственная Дума Федерального собрания Российской Федерации"

    def extract_resolution(self, paragraphs: list) -> str:
        for i, paragraph in enumerate(paragraphs):
            if paragraph.startswith("ПОСТАНОВЛЕНИЕ"):
                return self.clear_authority(paragraphs[i - 1 if i > 0 else i + 1])

            if "ЙЫШАНУ" in paragraph:
                return self.clear_authority(paragraphs[i - 2] if "ЧАВАШ" in paragraphs[i - 1] else paragraphs[i - 1])

            if "АДЫГЭ" in paragraph or "ЭЛЬКУН" in paragraph:
                return self.clear_authority(paragraphs[i - 1])

            if "ПОСТАНОВЛЕНИЕ" in paragraph:
                return self.clear_authority(paragraph[:paragraph.index("ПОСТАНОВЛЕНИЕ")])

        return self.clear_authority(paragraphs[0])

    def extract_disposal(self, paragraphs: list) -> str:
        for i, paragraph in enumerate(paragraphs):
            if paragraph.startswith("РАСПОРЯЖЕНИЕ"):
                return self.clear_authority(paragraphs[i - 1 if i > 0 else i + 1])

            if "РАСПОРЯЖЕНИЕ" in paragraph:
                return self.clear_authority(paragraph[:paragraph.index("РАСПОРЯЖЕНИЕ")])

        return self.clear_authority(paragraphs[0])

    def extract_law(self, paragraphs: list) -> str:
        for paragraph in paragraphs:
            if paragraph.startswith("Принят "):
                return self.clear_authority(paragraph[7:])

        return self.clear_authority(paragraphs[0])

    def extract_decree(self, paragraphs: list) -> str:
        for paragraph in paragraphs:
            if "ПРЕЗИДЕНТА РОССИЙСКОЙ ФЕДЕРАЦИИ" in paragraph:
                return self.clear_authority(paragraph)

        return self.clear_authority(paragraphs[0])

    def extract(self, text: str, doc_type: str) -> str:
        if doc_type == FEDERAL_LAW:
            return self.extract_federal_law()

        text = re.sub("РОССИЙСКАЯ ФЕДЕРАЦИЯ", "", text)

        text = text.replace("СКОИ", "СКОЙ")
        paragraphs = [self.__clear_paragraph(paragraph) for paragraph in re.findall(r"(?:.*\n)+?\n", text, re.M)]
        paragraphs = [paragraph for paragraph in paragraphs if paragraph]

        if doc_type == RESOLUTION:
            return self.extract_resolution(paragraphs)

        if doc_type == DECREE:
            return self.extract_decree(paragraphs)

        if doc_type == LAW:
            return self.extract_law(paragraphs)

        if doc_type == DISPOSAL:
            return self.extract_disposal(paragraphs)

        return self.clear_authority(paragraphs[0])
