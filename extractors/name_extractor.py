import re


class NameExtractor:
    def __init__(self, for_metric=True):
        self.strip_chars = " \n':|-" + ("\"" if for_metric else "")

    def clear_name(self, name: str) -> str:
        name = name.replace("'", "\"")
        name = re.sub("[|=*]", "", name)
        name = name.replace("_", " ")
        name = name.strip(self.strip_chars)

        if "\" в редакции" in name:
            name = name[:name.index("\" в редакции")]
        elif name.startswith("О законе") or name.startswith("О Законе") and " \"О" in name:
            name = name[name.index(" \"О")+2:]

        while "  " in name:
            name = name.replace("  ", " ")

        if name.endswith(" ."):
            name = name[:-2]

        return name

    def extract(self, text: str) -> str:
        if text[-1] != '\n':
            text += '\n'

        paragraphs = [paragraph.strip().replace("\n", " ") for paragraph in re.findall(r"(?:.*\n)+?\n", text, re.M)]
        text = "\n".join(paragraphs)

        names = re.findall(r"^О[бБ]? .+$", text, re.M)

        if names:
            return self.clear_name(names[0])

        names = re.findall(r"\bО[бБ]? .+$", text, re.M)

        if names:
            return self.clear_name(names[0])

        names = re.findall(r"^Вопросы .+$", text, re.M)

        if names:
            return self.clear_name(names[0])

        return "unknown name"