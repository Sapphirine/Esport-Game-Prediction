import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


raw_data = pd.read_csv('games.csv')
raw_data.info()
corr = raw_data.corr()
f,ax = plt.subplots(figsize=(32, 32))
sns.heatmap(corr, annot=True,  fmt= '.2f',ax=ax, annot_kws={'size': 12}, cmap=sns.color_palette("PuOr", 20))

ax.set_xlabel('Numeric features', size=20, color="#14A5CC")
ax.set_ylabel('Numeric features', size=20, color="#14A5CC")
ax.set_title('Correlation Between Features', size=24, color="#CC3366")

plt.show()

