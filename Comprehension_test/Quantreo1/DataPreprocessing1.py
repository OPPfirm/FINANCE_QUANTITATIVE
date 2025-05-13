# This file will be used to build a recurrent feature like technical indicator

# indicators.py – regroupement des indicateurs techniques réutilisables
import pandas as pd
import numpy as np
import ta

# === Moving Averages ===

def sma(df, col: str, n: int) -> pd.DataFrame:
    df = df.copy()
    df[f"SMA_{n}"] = ta.trend.SMAIndicator(df[col], int(n)).sma_indicator()
    return df

def ema(df, col: str, n: int) -> pd.DataFrame:
    df = df.copy()
    df[f"EMA_{n}"] = ta.trend.EMAIndicator(df[col], int(n)).ema_indicator()
    return df

def sma_diff(df, col: str, n: int, m: int) -> pd.DataFrame:
    df = df.copy()
    df[f"SMA_d_{n}"] = ta.trend.SMAIndicator(df[col], int(n)).sma_indicator()
    df[f"SMA_d_{m}"] = ta.trend.SMAIndicator(df[col], int(m)).sma_indicator()
    df["SMA_diff"] = df[f"SMA_d_{n}"] - df[f"SMA_d_{m}"]
    return df

# === Momentum Indicators ===

def rsi(df, col: str, n: int) -> pd.DataFrame:
    df = df.copy()
    df[f"RSI_{n}"] = ta.momentum.RSIIndicator(df[col], int(n)).rsi()
    return df

def sto_rsi(df, col: str, n: int) -> pd.DataFrame:
    df = df.copy()
    ind = ta.momentum.StochRSIIndicator(df[col], int(n))
    df["STO_RSI"] = ind.stochrsi() * 100
    df["STO_RSI_D"] = ind.stochrsi_d() * 100
    df["STO_RSI_K"] = ind.stochrsi_k() * 100
    return df

# === Volatility Indicators ===
def atr(df, n: int) -> pd.DataFrame:
    df = df.copy()
    atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], int(n))
    df[f"ATR_{n}"] = atr.average_true_range()
    return df

# === Trend Indicators ===
def ichimoku(df: pd.DataFrame, n1: int, n2: int) -> pd.DataFrame:
    df = df.copy()
    ichi = ta.trend.IchimokuIndicator(df["high"], df["low"], int(n1), int(n2))
    df["SPAN_A"] = ichi.ichimoku_a()
    df["SPAN_B"] = ichi.ichimoku_b()
    df["BASE"] = ichi.ichimoku_base_line()
    df["CONVERSION"] = ichi.ichimoku_conversion_line()
    return df

# === Return-Based Features ===
def previous_ret(df: pd.DataFrame, col: str, n: int) -> pd.DataFrame:
    df = df.copy()
    df["previous_ret"] = (df[col].shift(int(n)) - df[col]) / df[col]
    return df

# === Envelope / Deviation ===
def k_enveloppe(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    df = df.copy()
    df[f"EMA_HIGH_{n}"] = df["high"].ewm(span=n).mean()
    df[f"EMA_LOW_{n}"] = df["low"].ewm(span=n).mean()
    df["pivots_high"] = (df["close"] - df[f"EMA_HIGH_{n}"]) / df[f"EMA_HIGH_{n}"]
    df["pivots_low"] = (df["close"] - df[f"EMA_LOW_{n}"]) / df[f"EMA_LOW_{n}"]
    df["pivots"] = (df["pivots_high"] + df["pivots_low"]) / 2
    return df


# === Candlestick Info ===
def candle_information(df):
    # Candle color
    df["candle_way"] = -1
    df.loc[(df["open"] - df["close"]) < 0, "candle_way"] = 1

    # Filling percentage
    df["filling"] = np.abs(df["close"] - df["open"]) / np.abs(df["high"] - df["low"])

    # Amplitude
    df["amplitude"] = np.abs(df["close"] - df["open"]) / (df["open"] / 2 + df["close"] / 2) * 100

    return df

# === Machine Learning Prep ===
def data_split(df_model, split, list_X, list_y):
    # Train set creation
    X_train = df_model[list_X].iloc[0:split - 1, :]
    y_train = df_model[list_y].iloc[1:split]

    # Test set creation
    X_test = df_model[list_X].iloc[split:-1, :]
    y_test = df_model[list_y].iloc[split + 1:]

    return X_train, X_test, y_train, y_test

# === Labeling ===

def quantile_signal(df, n, quantile_level=0.67, pct_split=0.8):
    n = int(n)

    # Create the split between train and test set to do not create a Look-Ahead bias
    split = int(len(df) * pct_split)

    # Copy the dataframe to do not create any interference
    df_copy = df.copy()

    # Create the fut_ret column to be able to create the signal
    df_copy["fut_ret"] = (df_copy["close"].shift(-n) - df_copy["open"]) / df_copy["open"]

    # Create a column by name, 'Signal' and initialize with 0
    df_copy['Signal'] = 0

    # Assign a value of 1 to 'Signal' column for the quantile with the highest returns
    df_copy.loc[df_copy['fut_ret'] > df_copy['fut_ret'][:split].quantile(q=quantile_level), 'Signal'] = 1

    # Assign a value of -1 to 'Signal' column for the quantile with the lowest returns
    df_copy.loc[df_copy['fut_ret'] < df_copy['fut_ret'][:split].quantile(q=1 - quantile_level), 'Signal'] = -1

    return df_copy

def binary_signal(df, n):
    n = int(n)

    # Copy the dataframe to do not create any interference
    df_copy = df.copy()

    # Create the fut_ret column to be able to create the signal
    df_copy["fut_ret"] = (df_copy["close"].shift(-n) - df_copy["open"]) / df_copy["open"]

    # Create a column by name, 'Signal' and initialize with 0
    df_copy['Signal'] = -1

    # Assign a value of 1 to 'Signal' column for the quantile with the highest returns
    df_copy.loc[df_copy['fut_ret'] > 0, 'Signal'] = 1

    return df_copy
