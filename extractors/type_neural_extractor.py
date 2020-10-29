from typing import List
import numpy as np
import keras.backend as K
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, LeakyReLU, Dropout
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from constants import doc_types
from extractors.word_extractor import WordExtractor


class TypeNeuralExtractor:
    def __init__(self, load_weights=False):
        self.dictionary = self.__init_dictionary()
        self.labels = {doc_type: i for i, doc_type in enumerate(doc_types)}
        self.word_extractor = WordExtractor()

        self.input_size = len(self.dictionary)
        self.output_size = len(doc_types)

        self.initialization = 'he_normal'
        self.loss = 'categorical_crossentropy'
        self.learning_rate = 0.0001
        self.batch_size = 32
        self.epoches = 40
        self.verbose = 1
        self.test_part = 0

        self.weights_path = 'data/model_weights.h5'
        self.model = self.__init_model(load_weights)

    def __init_dictionary(self):
        with open("data/dictionary.txt", encoding='utf-8') as f:
            words = f.read().splitlines()

        dictionary = dict()

        for word in words:
            dictionary[word] = len(dictionary)

        return dictionary

    def recall_m(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision_m(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    def f1(self, y_true, y_pred):
        precision = self.precision_m(y_true, y_pred)
        recall = self.recall_m(y_true, y_pred)
        return 2 * ((precision * recall) / (precision + recall + K.epsilon()))

    def __init_model(self, load_weights: bool):
        model = Sequential()

        model.add(Dense(256, kernel_initializer=self.initialization, input_shape=(self.input_size,)))
        model.add(BatchNormalization())
        model.add(LeakyReLU(0.2))
        model.add(Dropout(0.3))

        model.add(Dense(64, kernel_initializer=self.initialization))
        model.add(BatchNormalization())
        model.add(LeakyReLU(0.2))
        model.add(Dropout(0.5))

        model.add(Dense(self.output_size, activation='softmax', kernel_initializer=self.initialization))

        optimizer = Adam(self.learning_rate)
        model.compile(optimizer, self.loss, ['acc', self.f1])

        if load_weights:
            model.load_weights(self.weights_path)

        return model

    def __text2vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.input_size)
        words = self.word_extractor.extract(text)

        for word in words:
            if word in self.dictionary:
                vec[self.dictionary[word]] += 1

        return vec

    def __label2vector(self, label: str) -> np.ndarray:
        vec = np.zeros(self.output_size)
        vec[self.labels[label]] = 1
        return vec

    def train_model(self, texts: List[str], labels: List[dict]):
        data_x = np.array([self.__text2vector(text) for text in texts])
        data_y = np.array([self.__label2vector(label["type"]) for label in labels])

        if self.test_part > 0:
            train_x, test_x, train_y, test_y = train_test_split(data_x, data_y, test_size=self.test_part)
            self.model.fit(train_x, train_y, self.batch_size, self.epoches, verbose=self.verbose, validation_data=(test_x, test_y))
        else:
            self.model.fit(data_x, data_y, self.batch_size, self.epoches, verbose=self.verbose)

        self.model.save_weights(self.weights_path)

    def extract(self, text: str) -> str:
        x = np.array([self.__text2vector(text)])
        y = self.model.predict(x)[0]

        return doc_types[np.argmax(y)]

    def extract_all(self, texts: List[str]) -> List[str]:
        x = np.array([self.__text2vector(text) for text in texts])
        y = self.model.predict(x)

        return [doc_types[np.argmax(yi)] for yi in y]
