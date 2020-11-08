from solution import Solution
from evaluators.eval_module import quality
from evaluators.accuracy_evaluator import AccuracyEvaluator
from data_reader import DataReader


def main():
    train_path = 'C:/Users/dronp/Documents/TPC/train'
    train_filename = 'gold_labels.txt'
    data, ids = DataReader().read_gold_data(train_path, train_filename)

    texts = [example[0] for example in data]
    labels = [example[1] for example in data]

    solution = Solution()
    predicted = solution.predict(texts)

    accuracy_evaluator = AccuracyEvaluator()
    accuracy_evaluator.evaluate(labels, predicted)

    print(quality(predicted, labels))


if __name__ == '__main__':
    main()
