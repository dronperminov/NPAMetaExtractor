import re
from constants import *


class NumberNormalizer:
    def __init__(self):
        pass

    def normalize(self, number: str, doc_type: str) -> str:
        number = re.sub(r"ПОСТАНОВЛЕНИЕ|ДУМЫ|ЗАКОНОДАТЕЛЬНОЕ", "", number)

        if doc_type == LAW:
            number = re.sub(r"[зЗ]3", "З", number)
            number = re.sub(r"-03", "-ОЗ", number)
            number = re.sub(r"-ТРЗ", "-ЗРТ", number)
        elif doc_type == RESOLUTION:
            if re.fullmatch(r"2\d\d\d(?:-пп)?", number.lower()):
                number = number[1:]

            number = re.sub("ппп|пл", "пп", number.lower())
            number = re.sub(r"-цг", "-пг", number.lower())
            number = re.sub(r"-пц", "-п", number.lower())
        elif doc_type == ORDER:
            number = re.sub("г$", "", number)

        number = number.replace(" ", "")

        return number