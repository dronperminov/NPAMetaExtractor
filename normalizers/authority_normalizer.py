import re


class AuthorityNormalizer:
    def __init__(self, strip_chars: str):
        self.strip_chars = strip_chars

        self.date_regexps = [
            re.compile(r"[0-3оО]?[\dоО].? *?[а-яА-ЯЁ][а-яА-ЯёЁ]+[\n\- ]*[12][09]\d\d(?: ?года)?"),
            re.compile(r"[0-3оО]?[\dоО][./, ][01о]?[\dоО][./, ] ?[12][09]\d\d(?: ?года)?")
        ]

        self.replace_regexps = [
            (re.compile("'"), "\""),
            (re.compile("[|=*:]"), ""),
            (re.compile("[_\n]| [,‚]"), " "),
            (re.compile("©"), "с"),
            (re.compile("ОЁ"), "Об"),
            (re.compile("Вв"), "в"),
            (re.compile(r" постановляет| постановление| приказ$| указ$| распоряжение$| статья| \)|\w+ созыва.*$|\d+.*? сессия"), "")
        ]

        self.normalize_regexps = [
            (re.compile(r"губернатора"), "губернатор"),
            (re.compile(r"^администрации"), "администрация"),
            (re.compile(r"главы"), "глава"),
            (re.compile(r"совета|советом"), "совет"),
            (re.compile(r"президента|президентом"), "президент"),
            (re.compile(r"думой"), "дума"),
            (re.compile(r"законодательным"), "законодательное"),
            (re.compile(r"законодательной"), "законодательная"),
            (re.compile(r"собранием"), "собрание"),
            (re.compile(r"стным"), "стное"),
            (re.compile(r"областной д"), "областная д"),
            (re.compile(r"ской областная"), "ская областная"),
            (re.compile(r"народным"), "народное"),
            (re.compile(r"собранием"), "собрание"),
            (re.compile(r"парламентом"), "парламент"),
            (re.compile(r"правительства"), "правительство"),
            (re.compile(r"правительство - "), "правительство "),
            (re.compile(r"государственным совет"), "государственный совет"),
            (re.compile(r"министерства"), "министерство"),
            (re.compile(r"управления"), "управление"),
            (re.compile(r"адыгэ республикэм"), "республики адыгея"),
            (re.compile(r" гыва"), " тыва"),
            (re.compile(r"мсмая"), "мская"),
            (re.compile(r"смолёнск"), "смоленск"),
            (re.compile(r" \(фтс россии\)"), ""),
            (re.compile(r" \(росстат\)"), ""),
            (re.compile(r" \(минспорт россии\)"), ""),
            (re.compile(r" \(минюст россии\)"), "")
        ]

    def normalize(self, authority: str) -> str:
        authority = authority.lower()

        for date_regexp in self.date_regexps:
            authority = date_regexp.sub("", authority)

        for regexp, replacement in self.replace_regexps:
            authority = regexp.sub(replacement, authority)

        authority = authority.strip(self.strip_chars)

        for regexp, replacement in self.normalize_regexps:
            authority = regexp.sub(replacement, authority)

        while "  " in authority:
            authority = authority.replace("  ", " ")

        if re.fullmatch(r".* [\w.]", authority):
            authority = authority[:-2]

        return authority
