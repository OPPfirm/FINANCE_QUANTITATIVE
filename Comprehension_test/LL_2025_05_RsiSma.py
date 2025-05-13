import pandas as pd

from Quantreo.DataPreprocessing import rsi, sma
#the thing i've imported from Quantreo is just a function to build the indicators (sma and rsi)
#that we will use in our strategy (in methode get_features)

"""
Notes:
time:is a timestamp ,here is a index of our DataFrame so we will use it to access the data
and find the signals
"""

class RsiSma:

    def __init__(self, data, parameters):
        """
        data: DataFrame containing OHLC data.
        parameters: Dictionary of strategy parameters.
        """
        self.data = data.copy()
        self.params = parameters  # Stocker le dict pour y accéder ensuite dans les méthodes



    def get_features(self):
        """Compute technical indicators (SMA fast/slow, RSI) and generate trade signals (column "signals."""

        fast_sma = self.params["fast_sma"]
        slow_sma = self.params["slow_sma"]
        rsi_period = self.params["rsi_period"]

        # Calculate indicators(rsi and sma return a data frame with a column for!)
        self.data = sma(self.data, "Close", fast_sma)
        self.data = sma(self.data, "Close", slow_sma)
        self.data = rsi(self.data, "Close", rsi_period)

        # Initialize columns
        self.data["signal"] = 0
        self.data["RSI_retarded"] = self.data["RSI"].shift(1)#df["col"].shit for -1 on the index
                                                             # (rember the end of our datset is the most recent)

        # Entry conditions
        condition_buy = (
                self.data[f"SMA_{fast_sma}"] < self.data[f"SMA_{slow_sma}"]
                & (self.data["RSI"] > self.data["RSI_retarded"])
        )
        condition_sell = (
                self.data[f"SMA_{fast_sma}"] > self.data[f"SMA_{slow_sma}"]
                & (self.data["RSI"] < self.data["RSI_retarded"])
        )

        self.data.loc[condition_buy, "signal"] = 1
        self.data.loc[condition_sell, "signal"] = -1

        return self.data


    def get_entry_signal(self, time):
        """
         Entry signal
         :param time: TimeStamp of the row
         :return: Entry signal of the row and entry time
        """
        # If we are in the first or second columns, we do nothing
        if len(self.data.loc[:time,:]) < 2:
            self.entry_time = None
            return 0, self.entry_time

        # Create entry signal --> -1,0,1
        entry_signal = 0
        if self.data.loc[:time,"signal"][-2] == 1:
            entry_signal = 1
        elif self.data.loc[:time,"signal"][-2] == -1:
            entry_signal = -1

        # Enter in buy position only if we want to, and we aren't already
        position = self.buy or self.sell
        if entry_signal == 1 and not position:
            self.buy = True
            self.open_buy_price = self.data.loc[time,"open"]
            self.entry_time = time

        # Enter in buy position only if we want to, and we aren't already
        elif entry_signal == -1 and not position:
            self.sell = True
            self.open_sell_price = self.data.loc[time,"open"]
            self.entry_time = time

        else:
            entry_signal = 0

        return entry_signal, self.entry_time


    def get_exit_signal(self, time):
        """
        Return the profit or loss at a given time index if a trade is closed.
        Only evaluates the PnL one bar after an entry.
        """

        pass





"""
RsiSma Class
The RsiSma class is designed to implement a trading strategy based 
on the RSI (Relative Strength Index) and two moving averages (SMA - Simple Moving Average). 
It aims to exploit divergences between market trends (SMAs) and market strength (RSI) to generate buy and sell signals.

Class Functions
__init__(self, data, parameters)

Description: Initializes the strategy with the necessary data and parameters.
Parameters:
data: A DataFrame containing market data.
parameters: A dictionary containing strategy parameters, such as SMA periods, RSI period,
Take Profit (TP) and Stop Loss (SL) thresholds, transaction cost, and leverage.
State Variables: Initializes variables to track trading positions (buy/sell), opening prices, entry and exit times, etc.
get_features(self)

Description: Calculates SMA and RSI indicators for the provided data.
Functionality:
Calculates fast and slow SMAs.
Calculates RSI.
Generates a trading signal based on the following conditions:
Buy: When the fast SMA is below the slow SMA (downward trend) and the current RSI is above the lagged RSI (upward force).
Sell: When the fast SMA is above the slow SMA (upward trend) and the current RSI is below the lagged RSI (downward force).
get_entry_signal(self, time)

Description: Generates the entry signal based on market conditions at a given time.
Parameters:
time: A timestamp representing the time for which the signal is generated.
Functionality:
Checks if a buy or sell signal should be generated.
Updates state variables to indicate that a position is open and records the opening price and entry time.
get_exit_signal(self, time)

Description: Generates the exit signal based on Take Profit (TP) and Stop Loss (SL) thresholds.
Parameters:
time: A timestamp representing the time for which the signal is generated.
Functionality:
Checks if an open position should be closed based on TP and SL thresholds.
Calculates the profit or loss of the position and updates state variables to indicate that the position is closed.

"""


"""
#-----------------------------------------------------------------------
# Example
# Initialize the strategy with data and parameters
parameters = {
    "fast_sma": 10,
    "slow_sma": 50,
    "rsi": 14,
    "tp": 0.05,
    "sl": -0.02,
    "cost": 0.001,
    "leverage": 10
}
strategy = RsiSma(data, parameters)

# Iterate over the data to get signals
for time in data.index:
    entry_signal, entry_time = strategy.get_entry_signal(time)
    exit_signal, exit_time = strategy.get_exit_signal(time)
    # Do something with the signals, e.g., execute trades

#------------------------------------------------------------------------------
"""








