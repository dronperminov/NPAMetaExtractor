from typing import List, Tuple
from normalizers.tesseract_normalizer import TesseractNormalizer
from normalizers.date_normalizer import DateNormalizer

from extractors.type_extractor import TypeExtractor
from extractors.date_extractor import DateExtractor
from extractors.number_extractor import NumberExtractor
from extractors.name_extractor import NameExtractor


class Solution:
    def __init__(self):
        self.tesseract_normalizer = TesseractNormalizer()
        self.date_normalizer = DateNormalizer()

        self.type_extractor = TypeExtractor()
        self.date_extractor = DateExtractor()
        self.number_extractor = NumberExtractor()
        self.name_extractor = NameExtractor()

    def train(self, train: List[Tuple[str, dict]]) -> None:
        pass

    def predict(self, test: List[str]) -> List[dict]:
        results = []

        for text in test:
            stripped_text = self.tesseract_normalizer.normalize(text)
            date_normalized_text = self.date_normalizer.normalize(stripped_text)
            normalized_text = self.tesseract_normalizer.normalize(text, strip_lines=False)

            doc_type = self.type_extractor.extract(date_normalized_text)
            date = self.date_extractor.extract(date_normalized_text, doc_type)
            number = self.number_extractor.extract(date_normalized_text, doc_type, date)
            name = self.name_extractor.extract(normalized_text)

            prediction = {"type": doc_type,
                          "date": date,
                          "number": number,
                          "authority": "",
                          "name": name}
            results.append(prediction)

        return results
