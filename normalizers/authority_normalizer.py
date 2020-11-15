import re


class AuthorityNormalizer:
    def __init__(self, strip_chars: str):
        self.strip_chars = strip_chars + ","

        self.date_regexps = [
            re.compile(r"[0-3оО]?[\dоО].? *?[а-яА-ЯЁ][а-яА-ЯёЁ]+[\n\- ]*[12][09] ?\d ?\d(?: ?года)?"),
            re.compile(r"[0-3оО]?[\dоО][./,\- ][01о]?[\dоО][./,\- ] ?[12][09] ?\d ?\d(?: ?года)?")
        ]

        self.replace_regexps = [
            (re.compile("'"), "\""),
            (re.compile(r"[|=*:/#&\]\[<>®$„«`^!]"), ""),
            (re.compile("[_\n]| [,‚]"), " "),
            (re.compile("©"), "с"),
            (re.compile("ОЁ"), "Об"),
            (re.compile("Вв"), "в"),
            (re.compile("[—–]"), "-"),
            (re.compile("--"), "-"),
            (re.compile(" но "), " по "),
            (re.compile("но "), "по "),
            (re.compile(r" постановляет| постановление| распоряжение| приказ| указ| статья| \)|\w+ созыва.*$|\d+.*? сессия"), "")
        ]

        self.normalize_regexps = [
            (re.compile(r"^губернатора"), "губернатор"),
            (re.compile(r"^администрации"), "администрация"),
            (re.compile(r"[гт]лавы"), "глава"),
            (re.compile(r"совета|советом"), "совет"),
            (re.compile(r"^президента|президентом"), "президент"),
            (re.compile(r"думой"), "дума"),
            (re.compile(r"законодательным"), "законодательное"),
            (re.compile(r"законодательной"), "законодательная"),
            (re.compile(r"^региональной"), "региональная"),
            (re.compile(r"службы"), "служба"),
            (re.compile(r"собранием"), "собрание"),
            (re.compile(r"стным"), "стное"),
            (re.compile(r"областной д"), "областная д"),
            (re.compile(r"ской областная"), "ская областная"),
            (re.compile(r"ской комисси[ий]"), "ская комиссия"),
            (re.compile(r"народным"), "народное"),
            (re.compile(r"собранием"), "собрание"),
            (re.compile(r"^народного собрания", re.I), "народное собрание"),
            (re.compile(r"парламентом|парламента"), "парламент"),
            (re.compile(r"^правительства"), "правительство"),
            (re.compile(r"правительство - "), "правительство "),
            (re.compile(r"правительств[ою]?[.,]"), "правительство"),
            (re.compile(r"государственным совет"), "государственный совет"),
            (re.compile(r"^государственной "), "государственная "),
            (re.compile(r" жилищной инспекции"), " жилищная инспекция"),
            (re.compile(r"испекции"), "инспекция"),
            (re.compile(r"министерства"), "министерство"),
            (re.compile(r"^управления"), "управление"),
            (re.compile(r"департамента "), "департамент "),
            (re.compile(r"адыгэ ?республикэм"), "республики адыгея"),
            (re.compile(r"хакас республиканы[не]?к?"), "республики хакасия"),
            (re.compile(r"(?:с )?буряад уласай"), "республики бурятия"),
            (re.compile(r"алтай республиканын"), "республики алтай"),
            (re.compile(r"саха ороспуубулукэтин"), "республики саха (якутия)"),
            (re.compile(r"кабинет министров .{1,4} республики"), "кабинет министров республики"),
            (re.compile(r" гыва"), " тыва"),
            (re.compile(r"мсмая"), "мская"),
            (re.compile(r"смолёнск"), "смоленск"),
            (re.compile(r" \(фтс россии\)"), ""),
            (re.compile(r" \(росстат\)"), ""),
            (re.compile(r" \((?:мин|управление|росстат|фтс россии).*?\)"), ""),
            (re.compile(" кра$"), " края"),
            (re.compile(" окр?у?г?$"), " округа"),
            (re.compile(" обл?а?с?т?$"), " области"),
            (re.compile(" республики адыгея республики адыгея"), " республики адыгея"),
            (re.compile("ая думы"), "ая дума"),
            (re.compile("^тлавное"), "главное")
        ]

    def normalize(self, authority: str) -> str:
        authority = authority.lower().replace("\\", "")

        for date_regexp in self.date_regexps:
            authority = date_regexp.sub("", authority)

        for regexp, replacement in self.replace_regexps:
            authority = regexp.sub(replacement, authority)

        authority = authority.strip(self.strip_chars)

        for regexp, replacement in self.normalize_regexps:
            authority = regexp.sub(replacement, authority)

        authority = re.sub(r" +", " ", authority)

        if re.fullmatch(r".* [\w.]", authority):
            authority = authority[:-2]

        return authority
