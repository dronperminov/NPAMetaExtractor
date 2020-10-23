import json
from typing import List, Dict, Tuple


class DataReader:
    def __init__(self):
        self.fixed = [
            "2664095bbfefac3294aa681a63824304d73c6a9e",
            "b56bedce48afa5ec79b3fb71cbd7718add89b0a7",
            "408e74823514366138b14d8ab61c7da6e211f6b7",
            "314f08619c13ddfd64480658316793bb5120e417",
            "8382e17f8991b216970bf779dd5a6e9d0fb7cbb8",
            "457bc4d86c65ee1df3ffe84300acfa3c408f8507",
            "bfd6b3e4c53c632bb98a512a7f17382fb0b225de",
            "0ff6c54442cdc14743c02e5e4b3345996c817219",
            "dd5812de5f5990890bf530cc9fb274463fa56e40",
            "20c4113ca499fbe92666349507a044e6dbfeefe5",
            "9317912026393eb9cf3f9f676208206622f5b835",
            "d7036c3ecd89b095e7372b0fbda9965dfafed51c",
            "14b4484c4ee3e1e44a076087c012e52ac71f91af",
            "7c2fa12a1a9075353cac2aa4e57b5544340fa183",
            "d8ee353cbbe155aadf94b549469d730d2815812c",
            "0a8ad767b089e5b931995b5741705fa8b537582d",
            "26718790b2f6c7d2c50c0b4a4ff5c41f835ed997",
            "8f8465680f58d2782898fdba54ea695d3baab53e",
            "c5285227de8b78cd4946e2ddf2098c03b0c6fcea",
            "234dbefd9f927bca62fddae01237623349956a9f",
            "54cf31d48ab7a8f708c0ef2f469c8445bceab722",
            "a4f2538a27a200f8ea1cce25d6df81fcebe341a6",
            "63774e205c8e91a7b9034967232000b207ecdbe5"
        ]

    def fix_row(self, row):
        if row["id"] in self.fixed:
            row["label"]["type"] = "постановление"

        return row

    # получение всей обучающей выборки
    def read_gold_data(self, path: str, filename: str, fix_labels=True) -> Tuple[List[Tuple[str, dict]], List[str]]:
        data, ids = [], []

        with open(path + '/' + filename, encoding='utf-8') as f:  # открываем файл
            for line in f:  # по строкам
                row = json.loads(line)

                if fix_labels:
                    row = self.fix_row(row)

                ids.append(row["id"])

                with open(path + "/txts/" + row["id"] + '.txt', encoding='utf-8') as train_file:
                    data.append((train_file.read(), row["label"]))

        return data, ids
