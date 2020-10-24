import re


class DateNormalizer:
    def __init__(self):
        self.date_regexps = [
            re.compile(r"\b[0-3]?[\dоО] *?[а-яА-Я][а-яА-Я]+[\n ](?:19|20)\d\d", re.M),
            re.compile(r"\b[0-3]?[\dоО]\.[01]?[\dоО]\.(?:19|20)\d\d", re.M),
            re.compile(r"\b[0-3]?[\dоО]/[01]?[\dоО]/(?:19|20)\d\d", re.M),
            re.compile(r"\b[0-3]?[\dоО] [01]?[\dоО] (?:19|20)\d\d", re.M),
        ]

        self.replace_regexps = [
            (re.compile(r"[\n ]+", re.M), " "),
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
        init_date = date

        for regexp, replacement in self.replace_regexps:
            date = regexp.sub(replacement, date)

        if not re.fullmatch(r"\d?\d\.\d?\d\.\d\d\d\d", date):
            return init_date

        parts = date.split('.')
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

        return '%02d.%02d.%04d' % (day, month, year)

    def normalize(self, text: str) -> str:
        normalized = ''
        begin_index = 0

        for regexp in self.date_regexps:
            matches = regexp.finditer(text)

            for match in matches:
                start, end = match.span()
                date = self.replace_date(text[start:end])
                normalized += text[begin_index:start] + date
                begin_index = end

        normalized += text[begin_index:]

        return normalized
