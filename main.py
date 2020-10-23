from solution import Solution
from eval_module import quality
from data_reader import DataReader


def main():
    train_path = 'C:/Users/dronp/Documents/TPC/train'
    train_filename = 'gold_labels.txt'
    data, ids = DataReader().read_gold_data(train_path, train_filename)

    texts = [example[0] for example in data]
    labels = [example[1] for example in data]

    solution = Solution()
    predicted = solution.predict(texts)

    solution.test(data)
    print(quality(predicted, labels))


if __name__ == '__main__':
    main()
