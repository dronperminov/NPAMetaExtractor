import re


class WordExtractor:
    def __init__(self):
        self.date_regexps = [
            re.compile(r"[0-3оО]?[\dоО].? *?[а-яА-Я][а-яА-Я]+[\n\- ]*[12][09]\d\d(?: ?года)?"),
            re.compile(r"[0-3оО]?[\dоО][./, ][01о]?[\dоО][./, ] ?[12][09]\d\d(?: ?года)?")
        ]

        self.number_regexp = re.compile(r"\d+ ?(?:-[а-я\d]+|[-/]\d+)*")
        self.word_regexp = re.compile(r"[а-яА-Яa-z][а-яА-Яa-z]+")

        with open("data/stop.txt", encoding='utf-8') as f:
            self.stop_words = f.read().splitlines()

    def extract(self, text: str):
        for date_regexp in self.date_regexps:
            text = date_regexp.sub(" date ", text)

        text = self.number_regexp.sub(" number ", text)
        words = self.word_regexp.findall(text.lower())

        return [word for word in words if word not in self.stop_words]
