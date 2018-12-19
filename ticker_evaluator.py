from collections import Counter
import numpy as np
from sklearn import svm, neighbors
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
import pandas as pd
from pathlib import Path


class TickerEvaluator:
    """"Evaluates a ticker with machine learning methods.
    The TickerEvaluator has features and labels.

    features -  the descriptive attributes. In this case the percentage change of
    the daily stock of each company from the given stock table.

    labels - attempting to predict. In this case we try to predict to buy,
    sell or hold a stock, based on the future days that are given.
    The values for the future days will be created by methods of machine learning,
    based on the given stock table data.
    """
    features = None
    label = None
    stock_table = None
    stock_tickers = []
    tickers = []
    ticker = None
    future_days = 0

    def __init__(self, stock_table, evaluate_tickers, future_days):
        self.stock_table = stock_table
        self.tickers = evaluate_tickers
        self.stock_tickers = stock_table.columns.values.tolist()
        self.future_days = future_days

    def add_data_for_label_to_stock_table(self):
        self.stock_table.fillna(0, inplace=True)

        for day in range(1, self.future_days + 1):
            label_data_col = '{}_{}d'.format(self.ticker, day)
            current_day = self.stock_table[self.ticker]
            last_day = current_day.shift(-day)
            percentage_diff_between_current_and_last_day = (current_day - last_day) / current_day

            self.stock_table[label_data_col] = percentage_diff_between_current_and_last_day

        self.stock_table.fillna(0, inplace=True)

    @staticmethod
    def buy_sell_hold(*days):
        days = [day for day in days]
        requirement = 0.02

        for col in days:
            if col > requirement:
                return 'buy'
            if col < -requirement:
                return 'sell'
        return 'hold'

    def create_features_and_label(self):
        label_name = '{}_target'.format(self.ticker)
        self.stock_table[label_name] = list(map(self.buy_sell_hold,
                                                self.stock_table['{}_1d'.format(self.ticker)],
                                                self.stock_table['{}_2d'.format(self.ticker)],
                                                self.stock_table['{}_3d'.format(self.ticker)],
                                                self.stock_table['{}_4d'.format(self.ticker)],
                                                self.stock_table['{}_5d'.format(self.ticker)],
                                                self.stock_table['{}_6d'.format(self.ticker)],
                                                self.stock_table['{}_7d'.format(self.ticker)]))

        features_values = self.stock_table[label_name].values.tolist()
        print('Data spread:', Counter(features_values))

        self.clean_up_stock_table()

        df_vals = self.stock_table[[ticker for ticker in self.stock_tickers]].pct_change()
        df_vals = df_vals.replace([np.inf, -np.inf], 0)
        df_vals.fillna(0, inplace=True)

        self.features = df_vals.values
        self.label = self.stock_table['{}_target'.format(self.ticker)].values

    def clean_up_stock_table(self):
        self.stock_table.fillna(0, inplace=True)
        self.stock_table.replace([np.inf, -np.inf], np.nan)
        self.stock_table.dropna(inplace=True)

    def evaluate(self):
        for ticker in self.tickers:
            self.ticker = ticker

            self.add_data_for_label_to_stock_table()
            self.create_features_and_label()

            features_train, features_test, label_train, label_test = train_test_split(
                self.features,
                self.label,
                test_size=0.25
            )

            clf = VotingClassifier([
                ('lsvc', svm.LinearSVC()),
                ('knn', neighbors.KNeighborsClassifier()),
                ('rfor', RandomForestClassifier(n_estimators=10))
            ])
            clf.fit(features_train, label_train)

            confidence = clf.score(features_test, label_test)
            predictions = clf.predict(features_test)

            self.result_output(confidence, predictions)

    @staticmethod
    def result_output(confidence, predictions):
        print('accuracy:', confidence)
        print('predicted class counts:', Counter(predictions))
        print()
        print()
