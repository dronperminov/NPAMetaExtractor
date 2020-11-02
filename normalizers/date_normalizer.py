import re
from datetime import datetime


class DateNormalizer:
    def __init__(self):
        date_regexps = [
            r"(?:\b[0-3оО]?[\dоО].? *?[а-яА-Я][а-яА-Я]+[\n ][12][09]\d\d)",
            r"(?:\b[0-3оО]?[\dоО][./, ][01о]?[\dоО][./, ] ?[12][09]\d\d)"
        ]

        self.date_regexps = re.compile("|".join(date_regexps), re.M)

        self.replace_regexps = [
            (re.compile(r"[\n,. ]+", re.M), " "),
            (re.compile(r"\. +"), "."),
            (re.compile(r" *?январ[яь] ?", re.I), ".01."),
            (re.compile(r" *?феврал[яь] ?", re.I), ".02."),
            (re.compile(r" *?март[а]? ?", re.I), ".03."),
            (re.compile(r" *?апрел[яь] ?", re.I), ".04."),
            (re.compile(r" *?ма[яй] ?", re.I), ".05."),
            (re.compile(r" *?июн[яь] ?", re.I), ".06."),
            (re.compile(r" *?июл[яь] ?", re.I), ".07."),
            (re.compile(r" *?август[а]? ?", re.I), ".08."),
            (re.compile(r" *?сентябр[яь] ?", re.I), ".09."),
            (re.compile(r" *?октябр[яь] ?", re.I), ".10."),
            (re.compile(r" *?ноябр[яь] ?", re.I), ".11."),
            (re.compile(r" *?декабр[яь] ?", re.I), ".12."),
            (re.compile(r"[оО]", re.I), "0"),
            (re.compile(r"[ /]+"), ".")
        ]

    def replace_date(self, date: str) -> str:
        for regexp, replacement in self.replace_regexps:
            date = regexp.sub(replacement, date)

        if not re.fullmatch(r"\d?\d\.\d?\d\.\d\d\d\d", date):
            return "[error_date]"

        parts = date.split('.')
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

        if day < 1 or day > 31 or month < 1 or month > 12 or year > 2025:
            return "[error_date]"

        if year > 2900:
            year -= 900

        try:
            datetime.strptime(date, '%d.%m.%Y')
        except ValueError:
            return "[error_date]"

        return '%02d.%02d.%04d' % (day, month, year)

    def normalize(self, text: str) -> str:
        normalized = ''
        begin_index = 0

        matches = self.date_regexps.finditer(text)

        for match in matches:
            start, end = match.span()
            date = self.replace_date(text[start:end])
            normalized += text[begin_index:start] + date
            begin_index = end

        normalized += text[begin_index:]

        return normalized
