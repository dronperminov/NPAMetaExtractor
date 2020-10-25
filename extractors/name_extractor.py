import re


class NameExtractor:
    def __init__(self):
        pass

    def clear_name(self, name: str) -> str:
        name = name.strip(" \n")

        if "\" в редакции" in name:
            name = name[:name.index("\" в редакции")]

        while "  " in name:
            name = name.replace("  ", " ")

        return name

    def extract(self, text: str) -> str:
        paragraphs = [paragraph.strip().replace("\n", " ") for paragraph in re.findall(r"(?:.*\n)+?\n", text, re.M) if paragraph]
        text = "\n".join(paragraphs)

        names = re.findall(r"^Об? .+\n", text, re.M)

        if names:
            return self.clear_name(names[0])

        names = re.findall(r"\bОб? .+\n", text, re.M)

        if names:
            return self.clear_name(names[0])

        return "unknown name"