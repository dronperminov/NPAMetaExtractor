from typing import List, Tuple
from normalizers.tesseract_normalizer import TesseractNormalizer
from normalizers.date_normalizer import DateNormalizer
from extractors.type_extractor import TypeExtractor
from extractors.date_extractor import DateExtractor


class Solution:
    def __init__(self):
        self.tesseract_normalizer = TesseractNormalizer()
        self.date_normalizer = DateNormalizer()

        self.type_extractor = TypeExtractor()
        self.date_extractor = DateExtractor()

    def normalize_text(self, text: str) -> str:
        text = self.tesseract_normalizer.normalize(text)
        text = self.date_normalizer.normalize(text)

        return text

    def train(self, train: List[Tuple[str, dict]]) -> None:
        pass

    def predict(self, test: List[str]) -> List[dict]:
        results = []

        for text in test:
            text = self.normalize_text(text)
            doc_type = self.type_extractor.extract(text)
            date = self.date_extractor.extract(text, doc_type)

            prediction = {"type": doc_type,
                          "date": date,
                          "number": "",
                          "authority": "",
                          "name": ""}
            results.append(prediction)

        return results

    def test(self, data: List[Tuple[str, dict]]) -> None:
        for i, (text, label) in enumerate(data):
            data[i] = (self.normalize_text(text), label)

        self.type_extractor.test_accuracies(data)
        self.date_extractor.test_accuracies(data)
