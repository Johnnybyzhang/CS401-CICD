import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pickle
import os
import requests

# Look for dataset in the data directory
dataset_path = os.path.join('data', 'dataset.csv')

# Check if the dataset exists, if not download it
if not os.path.exists(dataset_path):
    print(f"Dataset not found at {dataset_path}, downloading from remote source...")
    
    # URL for the dataset
    dataset_url = "https://homepages.dcc.ufmg.br/~cunha/hosted/cloudcomp-2023s2-datasets/2023_spotify_ds1.csv"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Download the file
    response = requests.get(dataset_url)
    with open(dataset_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Dataset downloaded and saved to {dataset_path}")

# Load only 2000 lines for quicker training
df = pd.read_csv(dataset_path)

# Print the size of the dataset
print(f"Dataset size: {df.shape}")
# Group the songs by playlist id (assuming 'pid' identifies each playlist)
basket = df.groupby('pid')['track_name'].apply(list).reset_index()

te = TransactionEncoder()
te_ary = te.fit(basket['track_name']).transform(basket['track_name'])
df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

# Find frequent itemsets with higher support threshold to reduce item combinations
frequent_itemsets = apriori(df_onehot, min_support=0.029, use_colnames=True, max_len=8)

# Use more stringent thresholds and filter earlier
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
# Limit number of rules if still too many
rules = rules.nlargest(5000000, 'confidence')

# Save the model to the data directory for persistence
model_path = os.path.join('data', 'model.pickle')
with open(model_path, 'wb') as f:
    pickle.dump(rules, f)
print(f"Model training complete, rules saved to {model_path}")