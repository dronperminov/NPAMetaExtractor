from typing import List, Callable
from constants import *


class AccuracyEvaluator:
    def __init__(self):
        self.fields = [
            ("type", lambda x, y: x == y),
            ("date", lambda x, y: x == y),
            ("number", lambda x, y: x == y),
            ("name", lambda x, y: x.replace(" ", "").lower() == y.replace(" ", "").lower()),
            ("authority", lambda x, y: x.replace(" ", "").lower() == y.replace(" ", "").lower())
        ]

    def __print_row(self, label: str, correct: int, total: int) -> None:
        part = '%d / %d' % (correct,  total)
        accuracy = correct / total
        incorrect = total - correct

        print('| %-21s | %13s | %10.8f | %9d |' % (label, part, accuracy, incorrect))

    def __print_results(self, label: str, correct: dict, total: dict):
        correct_all = 0
        total_all = 0

        print('+----------------------------------------------------------------+')
        print('| %-62s |' % (label + ' accuracy test:'))
        print('+-----------------------+---------------+------------+-----------+')
        print('|     Document type     |    Correct    |  Accuracy  | Incorrect |')
        print('+-----------------------+---------------+------------+-----------+')

        for doc_type in doc_types:
            if total[doc_type] == 0:
                continue

            self.__print_row(doc_type, correct[doc_type], total[doc_type])
            correct_all += correct[doc_type]
            total_all += total[doc_type]

        print('+-----------------------+---------------+------------+-----------+')
        self.__print_row('total', correct_all, total_all)
        print('+-----------------------+---------------+------------+-----------+\n')

    def evaluate_field(self, labels: List[dict], predictions: List[dict], field: str, compare: Callable) -> None:
        correct = {doc_type: 0 for doc_type in doc_types}
        total = {doc_type: 0 for doc_type in doc_types}
        correct_all = 0

        for label, prediction in zip(labels, predictions):
            if compare(label[field], prediction[field]):
                correct[label["type"]] += 1
                correct_all += 1

            total[label["type"]] += 1

        self.__print_results(field, correct, total)

    def evaluate(self, labels: List[dict], predictions: List[dict]) -> None:
        for (field, compare) in self.fields:
            self.evaluate_field(labels, predictions, field, compare)

