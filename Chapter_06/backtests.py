#!/bin/bash/env python3

# Python Script with Base Class
# for Event-Based Backtesting

# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH

import numpy as np
import pandas as pd
from pylab import mpl, plt
print(plt.style.available)
plt.style.use('tableau-colorblind10')
mpl.rcParams['font.family'] = 'serif'


class BaseBacktest(object):
    """ Base class for event-base backtesting of trading strategies

    Atributes
    =========
    symbol: str
        TR RIC (financial instrument) to be used
    start: str
        start date for data selection
    end: str
        end date for data selection
    amount: float
        amount to be invested either once or per trade
    ftc: float
        fixed transaction costs per trade (buy or sell)
    ptc: float
        proportional transaction costs per trade (buy or sell)

    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    plot_data:
        plots the closing price for the symbol
    get_data_price:
        returns the date and price for the given bar
    print_balance:
        prints out the current (cash) balance
    print_net_wealth:
        prints out the current net wealth
    place_by_order:
        places a buy order
    place_sell_order:
        places a sell order
    close_out:
        close out a long or short position
    """


    def __init__(self, symbol: str, start: str, end: str, amount: float,
                ftc=0.0, ptc=0.0, verbose=True) -> None:
                self.symbol = symbol
                self.start = start
                self.end = end
                self.initial_amount = amount
                self.amount = amount
                self.ftc = ftc
                self.ptc = ptc
                self.units = 0
                self.position = 0
                self.trades = 0
                self.verbose = verbose
                self.get_data()

    def get_data(self) -> None:
        """ Retrieves and prepares the base data set """
        raw = pd.read_csv('https://hilpisch.com/pyalgo_eikon_eod_data.csv',
                        index_col=0, parse_dates=True)
        raw = pd.DataFrame(raw[self.symbol])
        raw = raw.loc[self.start:self.end]
        raw.rename(columns={self.symbol: 'price'}, inplace=True)
        raw['returns'] = np.log(raw / raw.shift(1))
        self.data = raw.dropna()

    def plot_data(self) -> None:
        """ Plots the closing price for the symbol """
        self.data['price'].plot(figsize=(10, 6), title=self.symbol)

    def get_data_price(self, bar: int) -> tuple:
        """ Returns the date and price for the given bar """
        date = str(self.data.index[bar])[:10]
        price = self.data.price.iloc[bar]
        return date, price

    def print_balance(self, bar: int) -> None:
        """ Prints out the current (cash) balance """
        date, price = self.get_data_price(bar)
        print(f'{date} | Balance: {self.amount:.2f}')

    def print_net_wealth(self, bar: int) -> None:
        """ Prints out the current net wealth """
        date, price = self.get_data_price(bar)
        net_wealth = self.units * price + self.amount
        print(f'{date} | Net Wealth: {net_wealth:.2f}')

    def place_buy_order(self, bar: int, units=None, amount=None) -> None:
        """ Places a buy order """
        date, price = self.get_data_price(bar)
        if units is None:
            units = int(self.amount / price)
        self.amount -= (units * price) * (1 + self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f'{date} | BUY {units} {self.symbol} @ {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def place_sell_order(self, bar: int, units=None, amount=None) -> None:
        """ Places a sell order """
        date, price = self.get_data_price(bar)
        if units is None:
            units = int(amount / price)
        self.amount += (units * price) * (1 - self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(f'{date} | SELL {units} {self.symbol} @ {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def close_out(self, bar: int) -> None:
        """ Closing out a long or short position """
        date, price = self.get_data_price(bar)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(f'{date} | CLOSE OUT {self.symbol} @ {price:.2f}')
            print('=' * 55)
        print(f'Final Balance: {self.amount:.2f}')
        pref = ((self.amount - self.initial_amount) /
                self.initial_amount * 100)
        print(f'Profit / Return: {pref:.2f} %')
        print(f'Total Trades: {self.trades:.2f}')
        print('=' * 55)

if __name__ == "__main__":
    bb = BaseBacktest('EUR=', '2010-1-1', '2019-12-31', 100000)
    print(bb.data.info())
    print(bb.data.tail())
    bb.plot_data()
