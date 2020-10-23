from typing import List, Tuple


class Solution:
    def __init__(self):
        pass

    def train(self, train: List[Tuple[str, dict]]) -> None:
        pass

    def predict(self, test: List[str]) -> List[dict]:
        results = []

        for txt in test:
            prediction = {"type": "",
                          "date": "",
                          "number": "",
                          "authority": "",
                          "name": ""}
            results.append(prediction)

        return results
