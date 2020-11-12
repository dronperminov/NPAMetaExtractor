import re


class NameNormalizer:
    def __init__(self, strip_chars: str):
        self.strip_chars = strip_chars
        self.stop_words = ["\" в редакции", "Принят", "Статья", "Назначить", "Освободить", "Присвоить", "Включить",
                           "За активное", " в связи с жалоб", " в связи с запрос", " и пункта"]

        self.replace_regexps = [
            (re.compile("'"), "\""),
            (re.compile("[|=*‘]"), ""),
            (re.compile("_| [,‚]"), " "),
            (re.compile("©"), "с"),
            (re.compile("^ГО "), "О "),
            (re.compile("ОЁ"), "Об"),
            (re.compile("Вв"), "в"),
            (re.compile("-3С"), "-ЗС"),
            (re.compile("—"), "-")
        ]

    def normalize(self, name: str) -> str:
        for regexp, replacement in self.replace_regexps:
            name = regexp.sub(replacement, name)

        if (name.startswith("О законе") or name.startswith("О Законе")) and " \"О" in name:
            name = name[name.index(" \"О")+2:]
        elif name.startswith("по делу о") and re.search(r"\".*\"", name):
            name = re.findall(r"\"(.*)\"", name)[-1]

        name = name.strip(self.strip_chars)

        for word in self.stop_words:
            if word in name:
                name = name[:name.index(word)]

        name = re.sub(r" +", " ", name)

        if re.fullmatch(r".* [.уоО]|.*\".", name):
            name = name[:-2]

        return name.strip(' \"')
