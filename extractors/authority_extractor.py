import re
from constants import *
from normalizers.authority_normalizer import AuthorityNormalizer


class AuthorityExtractor:
    def __init__(self, for_metric=True):
        self.strip_chars = " \n':|-.,‚‘’°©^(" + ("\"" if for_metric else "")
        self.authority_normalizer = AuthorityNormalizer(self.strip_chars)

        self.authors = ["[пП]равительство", "Совет [Мм]инистров", "Президент", "Администрация", "Кабинет [Мм]инистров",
                        "Народное [сС]обрание", "Законодательное [Сс]обрание"]
        self.upper_authors = ["ПРАВИТЕЛЬСТВ[ОА]", "ГУБЕРНАТОРА?", "ДУМА\b", "Дума", "КАБИНЕТ МИНИСТРОВ", "ПРЕЗИДЕНТ",
                              r"ФЕДЕРАЛЬН(?:АЯ|ОЕ)(?: \w+,?)*", r"МИНИСТЕРСТВО(?: \w+,?)*$", "ГЛАВ[АЫ]", r"СОВЕТА?(?: \w+,?)*",
                              "ЗАКОНОДАТЕЛЬНОЕ СОБРАНИЕ", r"УПРАВЛЕНИЕ(?: \w+,?)*", r"КОМИТЕТ(?: \w+,?)*",
                              r"СЛУЖБА(?: \w+,?)*", r"ИНСПЕКЦИЯ(?: \w+,?)*", r"АППАРАТ(?: \w+,?)*", r"АГЕНТСТВО(?: \w+,?)*"]

        self.joined_authors = "|".join(self.authors)
        self.joined_upper_authors = "|".join(self.upper_authors)

        self.authority_regexps = [
            re.compile("((?:" + self.joined_authors + r")[ \n].*?(?:\n.*?)?) п ?остановляет"),
            re.compile(r"^((?:" + self.joined_upper_authors + r")\n{0,2}.+(?:\n(?:\w+ )?ОБЛАСТИ|\n(?:\w+ )?КРАЯ)?)\n", re.M),
            re.compile(r"((?:" + self.joined_authors + r")[ \n].*?(?:\n.*?)?)\nп ?остановляет"),

            re.compile("((?:" + self.joined_authors + r")[ \n].*?(?:\n.*?)?) ПОСТАНОВЛЯЕТ"),
            re.compile(r"((?:" + self.joined_authors + r")[ \n].*?(?:\n.*?)?)\nПОСТАНОВЛЯЕТ"),
            re.compile(r" постановлением (Губернатора[ \n].*?) от"),
            re.compile(r"[уУ]казом (Главы[ \n].*?) от"),
        ]

    def __clear_paragraph(self, paragraph: str) -> str:
        lines = paragraph.splitlines()

        for i, line in enumerate(lines):
            if len(line) < 5:
                line = ""

            lines[i] = re.sub("ФЕДЕРАЛЬНЫЙ ЗАКОН|У ?К ?А ?З|[ПН]{1,2} ?Р ?И ?К ?А ?З|ЗАКОН$", "", line)

            if re.fullmatch(r"[оО]т .+ №.+", lines[i]):
                lines[i] = ""

            lines[i] = lines[i].strip(self.strip_chars)

        return " ".join([line for line in lines if line]).strip()

    def is_good_paragraph(self, paragraph: str) -> bool:
        if not paragraph:
            return False

        if '№' in paragraph:
            return False

        return True

    def extract_federal_law(self) -> str:
        return "Государственная Дума Федерального собрания Российской Федерации"

    def extract_resolution(self, paragraphs: list, text: str) -> str:
        if "КОНСТИТУЦИОННОГО СУДА РОССИЙСКОЙ ФЕДЕРАЦИИ" in text:
            return "Конституционный Суд Российской Федерации"

        for i, paragraph in enumerate(paragraphs):
            if paragraph.startswith("ПОСТАНОВЛЕНИЕ ГУБЕРНАТОРА"):
                return self.authority_normalizer.normalize(paragraph[14:])

            if paragraph.startswith("ПОСТАНОВЛЕНИЕ"):
                return self.authority_normalizer.normalize(paragraphs[i - 1 if i > 0 else i + 1 if i < len(paragraphs) - 1 else i])

            if "ЙЫШАНУ" in paragraph:
                return self.authority_normalizer.normalize(paragraphs[i - 2] if "ЧАВАШ" in paragraphs[i - 1] else paragraphs[i - 1])

            if "АДЫГЭ" in paragraph or "ЭЛЬКУН" in paragraph:
                return self.authority_normalizer.normalize(paragraphs[i - 1])

            if "ПОСТАНОВЛЕНИЕ" in paragraph:
                return self.authority_normalizer.normalize(paragraph[:paragraph.index("ПОСТАНОВЛЕНИЕ")])

            if paragraph.endswith("постановляет:"):
                return self.authority_normalizer.normalize(paragraph)

        return self.authority_normalizer.normalize(paragraphs[0])

    def extract_disposal(self, paragraphs: list) -> str:
        for i, paragraph in enumerate(paragraphs):
            if paragraph.startswith("РАСПОРЯЖЕНИЕ"):
                return self.authority_normalizer.normalize(paragraphs[i - 1 if i > 0 else i + 1 if i < len(paragraphs) - 1 else i])

            if "РАСПОРЯЖЕНИЕ" in paragraph:
                return self.authority_normalizer.normalize(paragraph[:paragraph.index("РАСПОРЯЖЕНИЕ")])

        return self.authority_normalizer.normalize(paragraphs[0])

    def extract_law(self, paragraphs: list) -> str:
        for paragraph in paragraphs:
            if paragraph.startswith("Принят ") or paragraph.startswith("Привят "):
                return self.authority_normalizer.normalize(paragraph[7:])

        if re.fullmatch("ЗАКОН .* ОБЛАСТИ", paragraphs[0]):
            return self.authority_normalizer.normalize("Законодательная Дума " + paragraphs[0][6:])

        authority = self.authority_normalizer.normalize(paragraphs[0])

        if re.fullmatch("\w+ (?:области|края)", authority):
            authority = "Законодательная дума " + authority

        return authority

    def extract_decree(self, paragraphs: list, text: str) -> str:
        authorities = re.findall("указ.*\n(главы.*?)\n", text, re.I)

        if authorities:
            return self.authority_normalizer.normalize(authorities[0])

        authorities = re.findall("глава.*?\n(.*?)\nуказ", text, re.I)

        if authorities:
            return self.authority_normalizer.normalize("глава " + authorities[0])

        for paragraph in paragraphs:
            if "ПРЕЗИДЕНТА РОССИЙСКОЙ ФЕДЕРАЦИИ" in paragraph:
                return self.authority_normalizer.normalize(paragraph)

        return self.authority_normalizer.normalize(paragraphs[0])

    def extract(self, text: str, doc_type: str) -> str:
        if doc_type == FEDERAL_LAW:
            return self.extract_federal_law()

        text = re.sub("РОССИЙСКАЯ ФЕДЕРАЦИЯ", "", text)

        text = text.replace("СКОИ", "СКОЙ")
        paragraphs = [self.__clear_paragraph(paragraph) for paragraph in re.findall(r"(?:.*\n)+?\n", text, re.M)]
        paragraphs = [paragraph for paragraph in paragraphs if self.is_good_paragraph(paragraph)]

        for regexp in self.authority_regexps:
            authorities = regexp.findall(text)

            if authorities:
                return self.authority_normalizer.normalize(authorities[0])

        if doc_type == RESOLUTION:
            return self.extract_resolution(paragraphs, text)

        if doc_type == DECREE:
            return self.extract_decree(paragraphs, text)

        if doc_type == LAW:
            return self.extract_law(paragraphs)

        if doc_type == DISPOSAL:
            return self.extract_disposal(paragraphs)

        return self.authority_normalizer.normalize(paragraphs[0])
