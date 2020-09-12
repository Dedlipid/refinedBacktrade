"""
BOLU=MA(TP,n)+m∗σ[TP,n]
BOLD=MA(TP,n)−m∗σ[TP,n]
where:
BOLU=Upper Bollinger Band
BOLD=Lower Bollinger Band
MA=Moving average
TP (typical price)=(High+Low+Close)÷3
n=Number of days in smoothing period (typically 20)
m=Number of standard deviations (typically 2)
σ[TP,n]=Standard Deviation over last n periods of TP
"""
import pandas as pd
import matplotlib.pyplot as plt
S = pd.read_csv(filepath_or_buffer="C:\\Users\\bamsh\\Documents\\Assets\\HIS.csv",
                header=[0, 1], index_col=0,
                parse_dates=True)["EEM"].copy()

z1 = S["Close"].rolling(5).mean() + S["Close"].rolling(5).std()
z2 = S["Close"].rolling(5).mean() - S["Close"].rolling(5).std()
S["%b"] = (S["Close"]-z2)/(z1-z2)
print(S["%b"].tail())
