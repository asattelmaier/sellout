import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')

start = dt.datetime(2015, 1, 1)
end = dt.datetime.now()

df = web.DataReader("TSLA", "iex", start, end)

df.reset_index(inplace=True)
df.set_index("date", inplace=True)

if __name__ == '__main__':
    print(df.head())
