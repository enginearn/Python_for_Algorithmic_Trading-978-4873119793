#!/bin/bash/env python3

# PythonModule with Class
# for Vectorized Backtesting
# of Machine Learning-Based Strategy

# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH

import numpy as np
import pandas as pd
from sklearn import linear_model


class SKVectorBacktester(object):
    """ Class for the vectorized backtesting of
    machine learning-based trading strategies.

    Attributes
    ==========
    symbol: str
        TR RIC (financial instrument) with which to work with
    start: str
        start date for data selection
    end: str
        end date for data selection
    amount: int, float
        amount to be invested at the beginning
    tc: float
        proportional transaction costs (e.g., 0.5% = 0.005) per trade
    model: str
        either 'logistic' or 'regression' regression model

    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    select_data:
        selects a sub-set of the base data set
    prepare_features:
        prepares the features data for the model fitting
    fit_model:
        implements the fitting steps
    run_strategy:
        runs the backtest for the ML-based strategy
    plot_results:
        plots the cumulative returns of the strategy
        compared to the symbol
    """

    def __init__(self, symbol, start, end, amount, tc, model):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.amount = amount
        self.tc = tc
        self.results = None
        if model == 'regression':
            self.model = linear_model.LinearRegression()
        elif model == 'logistic':
            self.model = linear_model.LogisticRegression(
                C=1e6, solver='lbfgs', multi_class='ovr', max_iter=1000)
        else:
            raise ValueError('Model not known or not implemented yet.')
        self.get_data()

    def get_data(self):
        """ Retrieves and prepares the data.
        """
        raw = pd.read_csv('https://hilpisch.com/pyalgo_eikon_eod_data.csv',
                        index_col=0, parse_dates=True).dropna()
        raw = pd.DataFrame(raw[self.symbol])
        raw = raw.loc[self.start:self.end]
        raw.rename(columns={self.symbol: 'price'}, inplace=True)
        raw['returns'] = np.log(raw / raw.shift(1))
        self.data = raw.dropna()

    def select_data(self, start, end):
        """ Selects a sub-set of the base data set.
        """
        data = self.data[(self.data.index >= start) &
                        (self.data.index < end)].copy()
        return data

    def prepare_features(self, start, end):
        """Prepare the feature columns for the regression and prediction steps
        """
        self.data_subset = self.select_data(start, end)
        self.feature_columns = []
        for lag in range(1, self.lags + 1):
            col = f'lag_{lag}'
            self.data_subset[col] = self.data_subset['returns'].shift(lag)
            self.feature_columns.append(col)
        self.data_subset.dropna(inplace=True)

    def fit_model(self, start, end):
        """ Implements the fitting steps.
        """
        self.prepare_features(start, end)
        self.model.fit(self.data_subset[self.feature_columns],
                    np.sign(self.data_subset['returns']))

    def run_strategy(self, start_in, end_in, start_out, end_out, lags=3):
        """ Backtests the trading strategy.
        """
        self.lags = lags
        self.fit_model(start_in, end_in)
        # data = self.select_data(start_out, end_out)
        self.prepare_features(start_out, end_out)
        prediction = self.model.predict(self.data_subset[self.feature_columns])
        self.data_subset['prediction'] = prediction
        self.data_subset['strategy'] = (self.data_subset['prediction'] * \
                                        self.data_subset['returns'])
        # determine when a trade takes place
        trades = self.data_subset['prediction'].diff().fillna(0) != 0
        # subtract transaction costs from return when trade takes place
        self.data_subset['strategy'][trades] -= self.tc
        self.data_subset['creturns'] = (self.amount * \
                                        self.data_subset['returns'].cumsum().apply(np.exp))
        self.data_subset['cstrategy'] = (self.amount * \
                                        self.data_subset['strategy'].cumsum().apply(np.exp))
        self.results = self.data_subset
        # absolute performance of the strategy
        aperf = self.results['cstrategy'].iloc[-1]
        # out-/underperformance of strategy
        operf = aperf - self.results['creturns'].iloc[-1]
        return round(aperf, 2), round(operf, 2)

    def plot_results(self):
        """ Plots the cumulative performance of the trading strategy
        compared to the symbol.
        """
        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        else:
            title = f'{self.symbol} | TC = {self.tc:.4f}'
            self.results[['creturns', 'cstrategy']].plot(title=title, figsize=(10, 6))

if __name__ == '__main__':
    skvbt = SKVectorBacktester('.SPX', '2000-01-01', '2019-12-31',
                                10000, 0.0, 'regression')
    print(skvbt.run_strategy('2010-01-01', '2019-12-31',
                            '2010-01-01', '2019-12-31'))
    print(skvbt.run_strategy('2010-01-01', '2016-12-31',
                            '2017-01-01', '2019-12-31'))

    skvbt = SKVectorBacktester('.SPX', '2010-01-01', '2019-12-31',
                                10000, 0.0, 'logistic')
    print(skvbt.run_strategy('2010-01-01', '2019-12-31',
                            '2010-01-01', '2019-12-31'))
    print(skvbt.run_strategy('2010-01-01', '2016-12-31',
                            '2017-01-01', '2019-12-31'))

    skvbt = SKVectorBacktester('.SPX', '2010-01-01', '2019-12-31',
                                10000, 0.001, 'logistic')
    print(skvbt.run_strategy('2010-01-01', '2019-12-31',
                            '2010-01-01', '2019-12-31', lags=15))
    print(skvbt.run_strategy('2010-01-01', '2013-12-31',
                            '2014-01-01', '2019-12-31', lags=15))