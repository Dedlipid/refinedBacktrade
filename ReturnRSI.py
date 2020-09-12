from numpy import nan


def rsi(data, per):
    temp = data.copy()

    temp["diff"] = temp["Close"] - temp["Close"].shift(1)

    temp["G"], temp["L"] = temp["diff"].apply(lambda x: max(x, 0)), \
                           temp["diff"].apply(lambda x: -min(x, 0))

    temp["AG"] = temp["AL"] = nan

    first_day = temp["G"].first_valid_index()
    first_day_pos = temp.index.get_loc(first_day)

    temp.at[temp.index[first_day_pos + per - 1], "AG"] = \
        temp["G"][first_day:temp.index[first_day_pos+per-1]].mean()

    temp.at[temp.index[first_day_pos + 3], "AL"] = \
        temp["L"][first_day:temp.index[first_day_pos + 3]].mean()

    for items in temp.index[first_day_pos + 4:]:
        pos = temp.index.get_loc(items)
        temp.at[items, "AG"] = 0.25 * temp["G"][items] + 0.75 * temp["AG"][temp.index[pos - 1]]
        temp.at[items, "AL"] = (temp["L"][items] + 3 * temp["AL"][temp.index[pos - 1]]) / 4

    temp["RSI"] = (1 + temp["AL"] / temp["AG"]) ** (-1)
    return temp["RSI"]


if __name__ == '__main__':
    input("N PERIOD RSI CALCULATOR")
