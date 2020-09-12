import pandas as pd
import os
import yfinance as yf
from numpy import nan
import ReturnRSI
import matplotlib.pyplot as plt

T = pd.read_csv(filepath_or_buffer="Assets\\assets.csv")
T["Quantity"] = 0
T["last_buy"] = T["last_price"] = nan  # Index: Asst_name,Asst_quantity,Last_buy


plt.close()
plt.style.use("bmh")

# TODO:
#  1) Allocate cash based on available assets to buy that day
#  2) Have a history of prices so it's possible to measure success(per trade made, ie profit per trade)
#  3) Generalize the calc method to deal with certain bool dataFrames returned by the fetch method
#  4) Make fetch more efficient by using operations on whole dataFrames instead of looping through their elements


if os.path.isfile(
        "Assets\\HIS.csv"):

    his = pd.read_csv(
        filepath_or_buffer="Assets\\HIS.csv",
        header=[0, 1], index_col=0, parse_dates=True).swaplevel(1, 0, 1)
else:
    yf.download(T["Assets"].tolist())[
        ["Close", "High", "Low"]
    ].to_csv(path_or_buf="Assets\\HIS.csv")


class Strategy:
    def __init__(self, name, days, val):
        self.name = name
        self.days = days
        self.val = val
        self.balance_sheet = None
        self.his = None
        self.markers = ["Close"]
        if not self.check():
            self.fetch()
        else:
            self.his = pd.read_csv(filepath_or_buffer="Assets\\HIS_" +
                                   f"{self.name}.csv",
                                   header=[0, 1], index_col=0, parse_dates=True)

    def check(self):
        return os.path.isfile("Assets\\HIS_"+f'{self.name}.csv')

    def calc(self):
        if not self.check_balance():
            cash_total = self.val
            p = pd.DataFrame(index=self.his.index[-self.days:], columns=["AV", "C"])  # Date: Asst_val ,cash, total
            for day in range(self.days):
                for items in T.index.values:
                    pos = day - self.days
                    pos_index = self.his.index[pos]
                    v = cash_total / 5
                    temp = self.his.swaplevel(1, 0, 1)[T.iat[items, 0]]
                    q = max(round(v / temp.iat[pos, 1]), 0)
                    T.iat[items, 3] = temp.iat[pos, 1]

                    if q > 0:
                        if temp["BUY"][pos_index]:
                            cash_total -= temp.iat[pos, 1] * q
                            T.iat[items, 1] += q
                        if temp["AGR"][pos_index] and T.iat[items, 1] > 0:
                            cash_total -= temp.iat[pos, 1] * q
                            T.iat[items, 1] += q

                    if T.iat[items, 1] > 0:
                        if temp["SELL"][pos_index]:
                            cash_total += temp.iat[pos, 1] * T.iat[items, 1]
                            T.iat[items, 1] = 0

                T["V"] = T["Quantity"] * T["last_price"]
                p.iat[day, 0] = T["V"].sum()
                p.iat[day, 1] = cash_total
            p["TV"] = p["AV"] + p["C"]
            p.to_csv(
                path_or_buf="Profit%\\" +
                            f'p-{self.days}-{int(self.val)}-{self.name}.csv')
            self.balance_sheet = p

        return (f'cash={self.balance_sheet.iat[-1, 1]},'
                f'assets={self.balance_sheet.iat[-1, 0]},'
                f'p%={(self.balance_sheet.iat[-1, -1] - self.val) / self.val}')

    def fetch(self):
        return None

    def graph(self, *smoothing):
        self.calc()
        if smoothing:
            self.balance_sheet.rolling(smoothing[0]).mean().plot()
        else:
            self.balance_sheet.plot()
        plt.show()

    def get_balance(self):
        if self.balance_sheet is None:
            self.calc()
        return self.balance_sheet.copy()

    def check_balance(self):
        if os.path.isfile("Profit%\\" +
                          f'p-{self.days}-{int(self.val)}-{self.name}.csv'):
            self.balance_sheet = pd.read_csv(
                filepath_or_buffer="Profit%\\" +
                                   f'p-{self.days}-'
                                   f'{int(self.val)}-{self.name}.csv',
                                   index_col="Date",
                                   parse_dates=True)
            return True
        return False


class ThreeDayHiLow(Strategy):
    def __init__(self, day, vals):
        Strategy.__init__(self, "3dhl", day, vals)
        self.markers += ["HV", "LV", "STA", "LTA"]
        if not self.check():
            self.fetch()
        else:
            self.his = pd.read_csv(
                filepath_or_buffer="Assets\\HIS_3dhl.csv",
                                       header=[0, 1], index_col=0, parse_dates=True)

    def fetch(self):
        s = his.copy()
        for assets in T["Assets"]:
            s[assets, "STA"] = s[assets, "Close"].rolling(5).mean()
            s[assets, "LTA"] = s[assets, "Close"].rolling(200).mean()
            s[assets, "FALL"] = (s[assets, "High"] < s[assets, "High"].shift(1)) & \
                              (s[assets, "High"].shift(1) < s[assets, "High"].shift(2)) &\
                                (s[assets, "Low"] < s[assets, "Low"].shift(1)) & \
                              (s[assets, "Low"].shift(1) < s[assets, "Low"].shift(2))
            s[assets, "BUY"] = s[assets, "FALL"] & \
                               (s[assets, "STA"] > s[assets, "Close"]) & \
                               (s[assets, "Close"] > s[assets, "LTA"])

        s.to_csv(path_or_buf="Assets\\HIS_3dhl.csv")

        self.his = s

    def calc(self):
        if not self.check_balance():
            cash_total = self.val
            p = pd.DataFrame(
                index=self.his.index[-self.days:],
                columns=["AV", "C"])  # Date: Asst_val ,cash, total
            for day in range(self.days):

                for items in T.index.values:
                    v = cash_total / 5

                    pos = day - self.days

                    temp = self.his[T.iat[items, 0]]

                    q = max(round(v / temp.iat[pos, 0]), 0)

                    T.iat[items, 3] = temp.iat[pos, 0]
                    if cash_total > 0:
                        if T.iat[items, 1] > 0:

                            if temp.iat[pos, 0] >= temp.iat[pos, 3]:
                                cash_total += temp.iat[pos, 0] * T.iat[items, 1]
                                T.iat[items, 1] = 0

                            if temp.iat[pos, 0] <= T.iat[items, 2] and True:
                                cash_total -= temp.iat[pos, 0] * q
                                T.iat[items, 1] += q

                        if temp.iat[pos, 6]:
                            cash_total -= temp.iat[pos, 0] * q
                            T.iat[items, 1] += q
                            T.iat[items, 2] = temp.iat[pos, 0]

                T["V"] = T["Quantity"] * T["last_price"]
                p.iat[day, 0] = T["V"].sum()
                p.iat[day, 1] = cash_total

            p["TV"] = p["AV"] + p["C"]

            self.balance_sheet = p

            self.balance_sheet.to_csv(path_or_buf="Profit%\\" +
                                                  f'p-{self.days}-{int(self.val)}-{self.name}.csv')
        return (f'cash={self.balance_sheet.iat[-1, 1]},'
                f'assets={self.balance_sheet.iat[-1, 0]},'
                f'p%={(self.balance_sheet.iat[-1, -1] - self.val) / self.val}')


class RsiFour(Strategy):
    def __init__(self, day, vals):
        Strategy.__init__(self, "rsi4", day, vals)
        self.markers += ["RSI4"]

    def calc(self):
        if not self.check_balance():
            cash_total = self.val
            p = pd.DataFrame(index=self.his.index[-self.days:], columns=["AV", "C"])  # Date: Asst_val ,cash, total

            for day in range(self.days):
                for items in T.index.values:
                    v = cash_total/4
                    pos = day - self.days
                    temp = self.his[T.iat[items, 0]]
                    q = max(round(v / temp.iat[pos, 0]), 0)
                    T.iat[items, 3] = temp.iat[pos, 0]
                    if T.iat[items, 1] > 0:
                        if temp.iat[pos, 4] >= 0.55:
                            cash_total += temp.iat[pos, 0] * T.iat[items, 1]
                            T.iat[items, 1] = 0
                        if 0.20 >= temp.iat[pos, 4] and True:
                            cash_total -= temp.iat[pos, 1] * q
                            T.iat[items, 1] += q
                    if temp.iat[pos, 0] >= temp.iat[pos, 3] and 0.25 >= temp.iat[pos, 4]:
                        cash_total -= temp.iat[pos, 0] * q
                        T.iat[items, 1] += q
                T["V"] = T["Quantity"] * T["last_price"]
                p.iat[day, 0] = T["V"].sum()
                p.iat[day, 1] = cash_total
            p["TV"] = p["AV"] + p["C"]
            p.to_csv(
                path_or_buf="Profit%\\" +
                f'p-{self.days}-{int(self.val)}-{self.name}.csv')
            self.balance_sheet = p

        return (f'cash={self.balance_sheet.iat[-1, 1]},'
                f'assets={self.balance_sheet.iat[-1, 0]},'
                f'p%={(self.balance_sheet.iat[-1, -1] - self.val) / self.val}')

    def fetch(self):
        s = his.copy()
        for assets in T["Assets"]:
            s[assets, "LTA"] = s[assets, "Close"].rolling(200).mean()
            s[assets, "RSI4"] = ReturnRSI.rsi(s[assets], 4)
        s.to_csv(path_or_buf="Assets\\HIS_"+f"{self.name}.csv")
        self.his = s


class BeePercent(Strategy):
    def __init__(self, day, vals):
        Strategy.__init__(self, "b%", day, vals)
        self.markers += ["b%"]

    def fetch(self):

        s = his.copy()
        for assets in T["Assets"]:
            s[assets, "LTA"] = s[assets, "Close"].rolling(200).mean()
            n = 5
            z1 = s[assets, "Close"].rolling(n).mean() + \
                 s[assets, "Close"].rolling(n).std()
            z2 = s[assets, "Close"].rolling(n).mean() - \
                 s[assets, "Close"].rolling(n).std()
            s[assets, "%b"] = (s[assets, "Close"] - z2) / (z1 - z2)
            zee = s[assets, "%b"]
            s[assets, "3dl"] = (zee <= 0.2) & (zee.shift(1) <= 0.2) & (zee.shift(2) <= 0.2)
        s.to_csv(path_or_buf="Assets\\HIS_%b.csv")
        self.his = s

    def calc(self):

        if not self.check_balance():

            cash_total = self.val
            p = pd.DataFrame(index=self.his.index[-self.days:], columns=["AV", "C"])  # Date: Asst_val ,cash, total

            for day in range(self.days):

                for items in T.index.values:
                    v = cash_total / 5
                    pos = day - self.days
                    temp = self.his[T.iat[items, 0]]
                    q = max(round(v / temp.iat[pos, 0]), 0)
                    T.iat[items, 3] = temp.iat[pos, 0]
                    if T.iat[items, 1] > 0:
                        if temp.iat[pos, 4] >= 0.8:
                            cash_total += temp.iat[pos, 0] * T.iat[items, 1]
                            T.iat[items, 1] = 0
                        if 0.2 >= temp.iat[pos, 4] and True:
                            cash_total -= temp.iat[pos, 0] * q
                            T.iat[items, 1] += q

                    if temp.iat[pos, 0] >= temp.iat[pos, 3] and temp.iat[pos, 5]:
                        cash_total -= temp.iat[pos, 0] * q
                        T.iat[items, 1] += q

                T["V"] = T["Quantity"] * T["last_price"]
                p.iat[day, 0] = T["V"].sum()
                p.iat[day, 1] = cash_total

            p["TV"] = p["AV"] + p["C"]

            p.to_csv(
                path_or_buf="Profit%\\" +
                            f'p-{self.days}-{int(self.val)}-{self.name}.csv')
            self.balance_sheet = p

        return (f'cash={self.balance_sheet.iat[-1, 1]},'
                f'assets={self.balance_sheet.iat[-1, 0]},'
                f'p%={(self.balance_sheet.iat[-1, -1] - self.val) / self.val}')


if __name__ == '__main__':
    z = BeePercent(4500, 25000)
    print(z.calc())
    z.graph()
