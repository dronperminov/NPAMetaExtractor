import re
from datetime import datetime
from constants import *


class DateExtractor:
    def __init__(self):
        self.date_regexp = re.compile(r"[0-3]\d\.[01]\d\.[12][09]\d\d")
        self.start_date_regexp = re.compile(r"^[ —]*" + self.date_regexp.pattern, re.M)
        self.from_date_regexp = re.compile(r"^[оэО]т " + self.date_regexp.pattern, re.M)
        self.order_regexps = [
            re.compile(r"№.*\n^От *?" + self.date_regexp.pattern, re.M),
            re.compile(r"^ПРИКАЗ[\s\S\n]{0,50}?" + self.date_regexp.pattern, re.M),
            re.compile(self.date_regexp.pattern + r"[\s\S\n]{0,50}?^ПРИКАЗ\b", re.M),
            re.compile(r"^\s*" + self.date_regexp.pattern + r"(?: *г. *)?(?: № \d+-\w+)?$", re.M),
            re.compile(r"^От *?" + self.date_regexp.pattern, re.M),
            re.compile(r"протокол от " + self.date_regexp.pattern)
        ]

        self.law_regexp = re.compile(r"^" + self.date_regexp.pattern + r"(?!\s*\d\d:\d\d)")
        self.law_regexps = [
            re.compile(self.date_regexp.pattern + r".*\n.*\n*ПОСТАНОВЛЕНИЕ"),
            re.compile(r"^№? *\d+ ?[-—]? ?[Зз3]?\w*?\d* от " + self.date_regexp.pattern, re.M),
            re.compile(r"^" + self.date_regexp.pattern + r" (?:г\.|года)\n+?№ *\d+", re.M),
        ]
        self.decree_regexp = re.compile(r"^(?:[оО]т|г) *?" + self.date_regexp.pattern, re.M)
        self.decree_regexps = [
            re.compile(r"^(?:От|г) *?" + self.date_regexp.pattern, re.M),
            re.compile(r"^(?:от|г) *?" + self.date_regexp.pattern, re.M),
        ]
        self.disposal_regexps = [
            re.compile(r"^" + self.date_regexp.pattern + r" ?(?:[гт]|[гт]о[дл]а)\.?\n*?(?:№ ?\d+|\d+-р)", re.M),
            re.compile(r"^[оО]т " + self.date_regexp.pattern + r" № \d+/\d+(?:-рп?)?$", re.M),
            re.compile(r"^№ ?\d+[/\-\w]*(?: \d+/\d+\-\d+)?\n*?[оО]т ?" + self.date_regexp.pattern, re.M),
            re.compile(r"УТВЕРЖДЕНЫ[\s\S\n]{0,90}?от (" + self.date_regexp.pattern + ")", re.M),
            re.compile(r"РАСПОРЯЖЕНИЕ[\s\S\n]{0,45}?" + self.date_regexp.pattern, re.M),
            re.compile(r"обеспечивающих с " + self.date_regexp.pattern),
        ]
        self.resolution_regexps = [
            re.compile(r"ПОСТАНОВЛЕНИЕ[\s\S\n]{0,83}?(" + self.date_regexp.pattern + ")", re.M),
            re.compile(r"УТВЕРЖДЕН[ЫОА][\s\S\n]{0,180}?от (" + self.date_regexp.pattern + ")", re.M),
            re.compile(r"Настоящее постановление вступает в силу с " + self.date_regexp.pattern, re.M),
        ]

    def __extract_date(self, line: str) -> str:
        return self.date_regexp.findall(line)[0]

    def __extract_max_date(self, text: str):
        str_dates = self.date_regexp.findall(text)

        if not str_dates:
            return "unknown_date"

        dates = [datetime.strptime(date, '%d.%m.%Y') for date in str_dates]
        imax = 0

        for i, date in enumerate(dates):
            if date > dates[imax]:
                imax = i

        return str_dates[imax]

    def extract_federal_law(self, text: str) -> str:
        lines = text.splitlines()

        for line in lines[::-1]:
            if self.date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_order(self, text: str) -> str:
        for regexp in self.order_regexps:
            dates = regexp.findall(text)

            if dates:
                return self.__extract_date(dates[0])

        lines = [line for line in text.splitlines() if len(line) > 2]

        for line in lines[:5]:
            if self.date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_law(self, text: str) -> str:
        for regexp in self.law_regexps:
            dates = regexp.findall(text)

            if dates:
                return self.__extract_date(dates[0])

        if "ЗАКОНЫ" in text:
            text = text[:text.index("ЗАКОНЫ")]

        lines = [line for line in text.splitlines() if len(line) > 2]

        if len(lines) > 1 and self.date_regexp.search(lines[-2]):
            return self.__extract_date(lines[-2])

        for line in lines[-1:-10:-1]:
            if self.law_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[:20]:
            if re.fullmatch(self.date_regexp.pattern + r" .{0,3}№ \d+", line):
                return self.__extract_date(line)

        for line in lines[:6]:
            if self.law_regexp.search(line):
                return self.__extract_date(line)

        if len(lines) > 0 and self.date_regexp.search(lines[-1]):
            return self.__extract_date(lines[-1])

        return ""

    def extract_decree(self, text: str) -> str:
        dates = re.findall(r"В соответствии с рекомендациями [\s\S\n]*? от (" + self.date_regexp.pattern + ")", text)

        if dates:
            return dates[0]

        names = re.findall(r"^(?:О[бБ]?|\d+\.) (?:.*\n)+?\n", text, re.M)

        for name in names:
            text = text.replace(name, "")

        if "ПРИЛОЖЕНИЕ №" in text:
            text = text[:text.index("ПРИЛОЖЕНИЕ №")]

        if "РИСУНОК" in text:
            text = text[:text.index("РИСУНОК")]

        lines = [line for line in text.splitlines() if len(line) > 1]

        for line in lines[:3]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

            if self.decree_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[-1:-3:-1]:
            if self.decree_regexp.search(line):
                return self.__extract_date(line)

            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[::-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for regexp in self.decree_regexps:
            dates = regexp.findall(text)

            if dates:
                return self.__extract_date(dates[0])

        return ""

    def extract_disposal(self, text: str) -> str:
        for regexp in self.disposal_regexps:
            dates = regexp.findall(text)

            if dates:
                return self.__extract_date(dates[0])

        lines = [line for line in text.splitlines() if len(line) > 2]

        for line in lines[:4]:
            if self.start_date_regexp.search(line) or self.from_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[-1:-3:-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[::-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_resolution(self, text):
        lines = text.splitlines()

        if self.date_regexp.search(lines[0]):
            return self.__extract_date(lines[0])

        for regexp in self.resolution_regexps:
            dates = regexp.findall(text)

            if dates:
                return self.__extract_date(dates[0])

        for line in lines[-1:-3:-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[::-1]:
            if self.date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract(self, text: str, doc_type: str) -> str:
        all_dates = self.date_regexp.findall(text)

        if len(all_dates) == 1:
            return all_dates[0]

        extracted_date = ""

        if doc_type == FEDERAL_LAW:
            extracted_date = self.extract_federal_law(text)
        elif doc_type == ORDER:
            extracted_date = self.extract_order(text)
        elif doc_type == RESOLUTION:
            extracted_date = self.extract_resolution(text)
        elif doc_type == LAW:
            extracted_date = self.extract_law(text)
        elif doc_type == DECREE:
            extracted_date = self.extract_decree(text)
        elif doc_type == DISPOSAL:
            extracted_date = self.extract_disposal(text)

        return extracted_date if extracted_date else self.__extract_max_date(text)
