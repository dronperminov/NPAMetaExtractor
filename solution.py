from typing import List, Tuple
from normalizers.tesseract_normalizer import TesseractNormalizer
from normalizers.date_normalizer import DateNormalizer
from extractors.type_extractor import TypeExtractor


class Solution:
    def __init__(self):
        self.tesseract_normalizer = TesseractNormalizer()
        self.type_extractor = TypeExtractor()
        self.date_normalizer = DateNormalizer()

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

            prediction = {"type": doc_type,
                          "date": "",
                          "number": "",
                          "authority": "",
                          "name": ""}
            results.append(prediction)

        return results

    def test(self, data: List[Tuple[str, dict]]) -> None:
        for i, (text, label) in enumerate(data):
            data[i] = (self.tesseract_normalizer.normalize(text), label)

        self.type_extractor.test_accuracies(data)
