import re
from datetime import datetime
from typing import List, Tuple
from constants import *


class DateExtractor:
    def __init__(self):
        self.date_regexp = re.compile(r"[0-3]\d\.[01]\d\.[12][09]\d\d")
        self.start_date_regexp = re.compile(r"^" + self.date_regexp.pattern, re.M)
        self.order_regexps = [
            re.compile(self.date_regexp.pattern + r"[\s\S\n]{0,50}?ПРИКАЗ", re.M),
            re.compile(r"ПРИКАЗ[\s\S\n]{0,50}?" + self.date_regexp.pattern, re.M),
            re.compile(r"^От +?" + self.date_regexp.pattern, re.M),
        ]

        self.law_regexp = re.compile(r"^" + self.date_regexp.pattern + r"(?!\s*\d\d:\d\d)")
        self.decree_regexp = re.compile(r"^от +?" + self.date_regexp.pattern, re.M)
        self.disposal_regexp = re.compile(r"РАСПОРЯЖЕНИЕ[\s\S\n]{0,100}?" + self.date_regexp.pattern, re.M)
        self.resolution_regexp = re.compile(r"ПОСТАНОВЛЕНИЕ[\s\S\n]{0,100}?" + self.date_regexp.pattern, re.M)

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

        lines = text.splitlines()

        for line in lines[:5]:
            if self.date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_law(self, text: str) -> str:
        if re.search(r"ПОСТАНОВЛЯЕТ", text):
            text = text[:text.index("ПОСТАНОВЛЯЕТ")]  # sorry me...

        lines = text.splitlines()

        for line in lines[-1:-20:-1]:
            if self.law_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_decree(self, text: str) -> str:
        if re.search(r"ПОСТАНОВЛЯЮ", text):
            text = text[:text.index("ПОСТАНОВЛЯЮ")]  # sorry me...

        lines = text.splitlines()

        for line in lines[:5]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        for line in lines[::-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        dates = self.decree_regexp.findall(text)

        if dates:
            return self.__extract_date(dates[0])

        return ""

    def extract_disposal(self, text: str) -> str:
        lines = text.splitlines()

        for line in lines[-1:-3:-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        dates = self.disposal_regexp.findall(text)

        if dates:
            return self.__extract_date(dates[0])

        for line in lines[::-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        return ""

    def extract_resolution(self, text):
        lines = text.splitlines()

        if self.date_regexp.search(lines[0]):
            return self.__extract_date(lines[0])

        for line in lines[-1:-3:-1]:
            if self.start_date_regexp.search(line):
                return self.__extract_date(line)

        dates = self.resolution_regexp.findall(text)

        if dates:
            return self.__extract_date(dates[0])

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

    def test_accuracies(self, data: List[Tuple[str, dict]]):
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}
        correct_all = 0

        for example in data:
            text, label = example
            date = self.extract(text, label["type"])

            if label["date"] == date:
                correct[label["type"]] += 1
                correct_all += 1

            total[label["type"]] += 1

        print("\nDate extractor accuracy test:")
        for doc_type in doc_types:
            print(f'{doc_type}: {correct[doc_type]} / {total[doc_type]} ({correct[doc_type] / total[doc_type]}, error: {total[doc_type] - correct[doc_type]})')

        print(f'Total: {correct_all} / {len(data)} ({correct_all / len(data)})')
