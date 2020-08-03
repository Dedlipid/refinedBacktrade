import pandas as pd
import os
import yfinance as yf
from numpy import nan

T = pd.read_csv("assets.csv")
T["Quantity"] = 0
T["last_buy"] = T["last_price"] = nan  # Index: Asst_name,Ass_quantity,Last_price


def init():
    """
    Gets and updates data of tracked assets, which are kept in assets.csv
    As of now, assets in assets.csv have to be initialized or removed by hand
    """
    t = pd.read_csv("assets.csv")
    if not os.path.isfile('./HIS.csv'):
        yf.download(t["Assets"].tolist()).swaplevel(1, 0, 1).to_csv("HIS.csv")
    s = pd.read_csv("HIS.csv", header=[0, 1], index_col=0)

    for assets in t["Assets"]:
        s[assets, "STA"] = s[assets, "Close"].rolling(5).mean()
        s[assets, "LTA"] = s[assets, "Close"].rolling(200).mean()
        s[assets, "HV"] = (s[assets, "High"] < s[assets, "High"].shift(1)) & \
                          (s[assets, "High"].shift(1) < s[assets, "High"].shift(2))
        s[assets, "LV"] = (s[assets, "Low"] < s[assets, "Low"].shift(1)) & \
                          (s[assets, "Low"].shift(1) < s[assets, "Low"].shift(2))
    s.to_csv("HIS_USE.csv")


if not os.path.isfile('./HIS_USE.csv'):
    init()

S = pd.read_csv("HIS_USE.csv", header=[0, 1], index_col=0)


def calc(days, cash, gen_csv):
    """
    Runs through the days and assets, calculating the daily net worth, using the hardcoded
    trading strategy, and finally return the final standings, including the percentage profit
    """
    cash_total = cash
    p = pd.DataFrame(index=S.index[-days:], columns=["AV", "C"])  # Date: Asst_val ,cash, total

    for day in range(days):

        for items in T.index.values:
            v = cash_total / 5

            pos = day - days

            temp = S[T.iat[items, 0]]

            q = max(round(v / temp.iat[pos, 1]), 0)

            T.iat[items, 3] = temp.iat[pos, 1]

            if T.iat[items, 1] > 0:

                if temp.iat[pos, 1] >= temp.iat[pos, 6]:
                    cash_total += temp.iat[pos, 1] * T.iat[items, 1]
                    T.iat[items, 1] = 0

                if temp.iat[pos, 1] <= T.iat[items, 2] and True:
                    cash_total -= temp.iat[pos, 1] * q
                    T.iat[items, 1] += q

            if temp.iat[pos, 8] and temp.iat[pos, 9]:

                if temp.iat[pos, 6] >= temp.iat[pos, 1] >= temp.iat[pos, 7]:
                    cash_total -= temp.iat[pos, 1] * q
                    T.iat[items, 1] += q
                    T.iat[items, 2] = temp.iat[pos, 1]

        T["V"] = T["Quantity"] * T["last_price"]
        p.iat[day, 0] = T["V"].sum()
        p.iat[day, 1] = cash_total

    p["TV"] = p["AV"] + p["C"]

    if gen_csv:
        p.to_csv(f'p-{days}-{cash}.csv')
    return (f'cash={p.iat[-1, 1]},'
            f'assets={p.iat[-1, 0]},'
            f'p%={(p.iat[-1,-1] - cash) / cash}')


if __name__ == '__main__':
    i = input("").split(" ")
    print(calc(int(i[0]), float(i[1]), bool(i[2])))
    input("")
