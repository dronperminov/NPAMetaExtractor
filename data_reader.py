import json
from typing import List, Tuple


class DataReader:
    def __init__(self):
        pass

    # получение всей обучающей выборки
    def read_gold_data(self, path: str, filename: str) -> Tuple[List[Tuple[str, dict]], List[str]]:
        data, ids = [], []

        with open(path + '/' + filename, encoding='utf-8') as f:  # открываем файл
            for line in f:  # по строкам
                row = json.loads(line)
                ids.append(row["id"])

                with open(path + "/txts/" + row["id"] + '.txt', encoding='utf-8') as train_file:
                    data.append((train_file.read(), row["label"]))

        return data, ids
