import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pickle

# Load only 5000 lines for quicker training
df = pd.read_csv('dataset.csv', nrows=5000)

# Group the songs by playlist id (assuming 'pid' identifies each playlist)
basket = df.groupby('pid')['track_name'].apply(list).reset_index()

te = TransactionEncoder()
te_ary = te.fit(basket['track_name']).transform(basket['track_name'])
df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

# Find frequent itemsets – you can adjust the support threshold as needed
frequent_itemsets = apriori(df_onehot, min_support=0.01, use_colnames=True)
# Generate association rules based on a confidence threshold (e.g., 0.5)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

with open('model.pickle', 'wb') as f:
    pickle.dump(rules, f)
print("Model training complete, rules saved to model.pickle.")