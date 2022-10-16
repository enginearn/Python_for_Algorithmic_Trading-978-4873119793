#!/bin/bash/env python3

# Python Script with Long Only Class
# for Event-Based Backtesting

# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH

from backtests import *

class BacktestLongOnly(BaseBacktest):
    def run_sma_strategy(self, SMA1: int, SMA2: int) -> None:
        """ Backtesting an SMA-based strategy.

        Parameters
        ==========
        SMA1: int
            short moving average
        SMA2: int
            long moving average
        """
        msg = f'\n\nRunning SMA strategy | SMA1 = {SMA1} & SMA2 = {SMA2}'
        msg += f'\nfixed costs {self.ftc} |'
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        self.position = 0 # initial neutral position
        self.trades = 0 # no trades yet
        self.amount = self.initial_amount # reset initial capital
        self.data['SMA1'] = self.data['price'].rolling(SMA1).mean()
        self.data['SMA2'] = self.data['price'].rolling(SMA2).mean()

        for bar in range(SMA2, len(self.data)):
            if self.position == 0:
                if self.data['SMA1'].iloc[bar] > \
                        self.data['SMA2'].iloc[bar]:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1 # long position
                elif self.position == 1:
                    if self.data['SMA1'].iloc[bar] < \
                            self.data['SMA2'].iloc[bar]:
                        self.place_sell_order(bar, units=self.units)
                        self.position = 0 # market neutral
        self.close_out(bar)

    def rum_momentum_strategy(self, momentum: int) -> None:
        """ Backtesting a momentum-based strategy.

        Parameters
        ==========
        momentum: int
            number of bars for momentum calculation
        """
        msg = f'\n\nRunning momentum strategy | momentum = {momentum} days'
        msg += f'\nfixed costs {self.ftc} |'
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        self.position = 0 # initial neutral position
        self.trades = 0 # no trades yet
        self.amount = self.initial_amount # reset initial capital
        self.data['momentum'] = self.data['return'].rolling(momentum).mean()
        for bar in range(momentum, len(self.data)):
            if self.position == 0:
                if self.data['momentum'].iloc[bar] > 0:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1 # long position
            elif self.position == 1:
                if self.data['momentum'].iloc[bar] < 0:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0 # market neutral
        self.close_out(bar)

    def run_mean_reversion_strategy(self, SMA: int, threshold: float) -> None:
        """ Backtesting a mean-reversion strategy.

        Parameters
        ==========
        SMA: int
            number of bars for SMA calculation
        threshold: float
            threshold for mean-reversion
        """
        msg = f'\n\nRunning mean-reversion strategy | '
        msg += f'SMA = {SMA} days | threshold = {threshold}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount

        self.data['SMA'] = self.data['price'].rolling(SMA).mean()

        for bar in range(SMA, len(self.data)):
            if self.position == 0:
                if (self.data['price'].iloc[bar] < \
                        self.data['SMA'].iloc[bar] - threshold):
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if self.data['price'].iloc[bar] > \
                        self.data['SMA'].iloc[bar]:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0
        self.close_out(bar)

if __name__ == '__main__':
    # backtesting a long-only strategy
    def run_strategies():
        lobt.run_sma_strategy(SMA1=42, SMA2=252)
        lobt.run_momentum_strategy(momentum=60)
        lobt.run_mean_reversion_strategy(SMA=50, threshold=5)

    lobt = BacktestLongOnly('SPY', '2010-1-1', '2018-1-1',
                            10000, verbose=False)
    run_strategies()
    # transaction costs: 10 USD fix, 1% variable
    lobt = BacktestLongOnly('SPY', '2010-1-1', '2018-1-1',
                            10000, ftc=10, ptc=0.01, verbose=False)
    run_strategies()
