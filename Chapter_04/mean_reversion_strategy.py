#!/bin/bash/env python3

# Python Module with Class
# for Vectorized Backtesting
# of Mean-Reversion Strategies
# Python for Algorithmic Trading 2nd ed.
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH

from ctypes.wintypes import SMALL_RECT
from momentum_strategy import *


class MeanReversionStrategy(MomVectorBacktester):
    ''' Class for the vectorized backtesting of
    mean reversion-based trading strategies.

    Attributes
    ==========
    symbol: str
        RCI symbol with which to work with
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    amount: int, float
        amount to be invested at the beginning
    tc: float
        proportional transaction costs (e.g., 0.5% = 0.005) per trade

    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    run_strategy:
        runs the backtest for the mean-reversion strategy
    plot_results:
        plots the cumulative performance of the strategy
        compared to the symbol
    '''


    def run_strategy(self, SMA, threshold):
        """ Backtests the trading strategy.
        """
        self.sma = SMA
        self.threshold = threshold
        data = self.data.copy().dropna()
        data['sma'] = data['price'].rolling(SMA).mean()
        data['distance'] = data['price'] - data['sma']
        data.dropna(inplace=True)
        # sell signals
        data['position'] = np.where(data['distance'] > threshold, -1, np.nan)
        # buy signals
        data['position'] = np.where(data['distance'] < -threshold, 1, data['position'])
        # crossing of current price  and SMA (zero distance)
        data['position'] = np.where(data['distance'] * data['distance'].shift(1) < 0, 0, data['position'])
        # filling the NaN values
        data['position'] = data['position'].ffill().fillna(0)
        data['strategy'] = data['position'].shift(1) * data['returns']
        # determine when a trade takes place
        trades = data['position'].diff().fillna(0) != 0
        # subtract transaction costs from return when trade takes place
        data['strategy'][trades] -= self.tc
        data['creturns'] = self.amount * data['returns'].cumsum().apply(np.exp)
        data['cstrategy'] = self.amount * data['strategy'].cumsum().apply(np.exp)
        self.results = data
        # absolute performance of the strategy
        aperf = self.results['cstrategy'].iloc[-1]
        # out-/underperformance of strategy
        operf = aperf - self.results['creturns'].iloc[-1]
        return round(aperf, 2), round(operf, 2)

    def plot_results(self):
        """Plots the cumulative performance of the strategy
        compared to the symbol."""
        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        else:
            title = f'{self.symbol} | TC = {self.tc:.4f} | SMA = {self.sma} | Threshold = {self.threshold}'
            self.results[['creturns', 'cstrategy']].plot(title=title, figsize=(10, 6))


if __name__ == '__main__':
    mrbt = MeanReversionStrategy('GDX', '2010-1-1', '2020-12-31', 10000, 0.0)
    print(mrbt.run_strategy(SMA=25, threshold=5))
    mrbt = MeanReversionStrategy('GDX', '2010-1-1', '2020-12-31', 10000, 0.001)
    print(mrbt.run_strategy(SMA=25, threshold=5))
    mrbt = MeanReversionStrategy('GLD', '2010-1-1', '2020-12-31', 10000, 0.005)
    print(mrbt.run_strategy(SMA=42, threshold=7.5))
