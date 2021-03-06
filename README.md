# A refined implementation of [simpleBackTrade](https://github.com/Dedlipid/simpleBackTrade)

The data gathering has been sped up substancially(from minutes to seconds). The data is processed on a day by day basis instead of a fund 
by fund basis, allowing visualizations of things like the total cash, asset value, and profits. The asset csv has also been made
easier to edit. Same parameters as before are variable.

# Getting Started
- Download DailyPrft.py and assets.csv into the same folder, and just indicate to the daily profit file the timespan(int), starting cash(float),
and weather you want the daily data saved to a csv(bool), seperated by a comma, and enjoy the results.

# Built With
- **The environment:** [PyCharm IDE](https://www.jetbrains.com/pycharm/)
- **Data Processing:** [Pandas](https://pandas.pydata.org/),[numpy](https://numpy.org/),and [yfinance](https://pypi.org/project/yfinance/) 
- **Education:** [High Probability ETF Trading: 7 Professional Strategies To Improve Your ETF Trading](https://www.amazon.ca/High-Probability-ETF-Trading-Professional/dp/0615297412/ref=sr_1_3?dchild=1&keywords=alvarez+trading+7&qid=1595478172&sr=8-3)

# Challenges
Getting famaliar with manuplating multi-index data, re-adjusting indicies, and considering where to store related data in DataFrames.

# Next Steps For Improvement
- Add the shorting strategy(dependant on the rates one's broker gives) 
- Allocate cash based on available assets to buy that day
- Have a history of prices so it's possible to measure success(per trade made, ie profit per trade)
- Generalize the calc method to deal with certain bool dataFrames returned by the fetch method
-Make fetch more efficient by using operations on whole dataFrames instead of looping through their elements

# Author
- **Bamdad Shamaei** [Github](https://github.com/Dedlipid/)

# License
- This project is licensed under the MIT License, see the [LICENSE.txt](https://github.com/rikardsaqe/Movie-Recommendation-Tools/blob/master/LICENSE) file for details
