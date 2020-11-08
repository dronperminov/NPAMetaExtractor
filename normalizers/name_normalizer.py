import re


class NameNormalizer:
    def __init__(self, strip_chars: str):
        self.strip_chars = strip_chars
        self.stop_words = ["\" в редакции", "Принят", "Статья", "Назначить", "Освободить", "Присвоить", "Включить",
                           "За активное", " в связи с жалоб", " в связи с запрос", " и пункта"]

        self.replace_regexps = [
            (re.compile("'"), "\""),
            (re.compile("[|=*]"), ""),
            (re.compile("_| [,‚]"), " "),
            (re.compile("©"), "с"),
            (re.compile("ОЁ"), "Об"),
            (re.compile("Вв"), "в")
        ]

    def normalize(self, name: str) -> str:
        for regexp, replacement in self.replace_regexps:
            name = regexp.sub(replacement, name)

        name = name.strip(self.strip_chars)

        if name.startswith("О законе") or name.startswith("О Законе") and " \"О" in name:
            name = name[name.index(" \"О")+2:]

        for word in self.stop_words:
            if word in name:
                name = name[:name.index(word)]

        while "  " in name:
            name = name.replace("  ", " ")

        if re.fullmatch(r".* [.уоО]|.*\".", name):
            name = name[:-2]

        return name.strip(' \"')
