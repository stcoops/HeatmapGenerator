from github import Github # type: ignore
import pandas as pd # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore 
from matplotlib.colors import LinearSegmentedColormap # type: ignore
import matplotlib.dates as mdates #type: ignore
from datetime import datetime, timedelta
import os
import numpy as np #type: ignore

# GitHub personal access token from environment variable
token = os.getenv('GH_TOKEN')
g = Github(token)

# Your GitHub username
#username = os.getenv("GH_USERNAME")

# For Testing:
username = "stcoops"
# Get all your public repositories
user = g.get_user()
repos = user.get_repos()

commit_dates = []

for repo in repos:
    try:
        commits = repo.get_commits(author=username)
        for commit in commits:
            date = commit.commit.author.date.strftime("%Y-%m-%d")
            commit_dates.append(date)
    except Exception as e:
        print(f"Error fetching commits from {repo.name}: {e}")
        print("Possible no commits on repo?")
        pass

# Count commits per date
if not commit_dates:
    print("No commits found.")
    exit(1)

date_series = pd.Series(commit_dates)
commit_counts = date_series.value_counts().sort_index()

# Convert to DataFrame
df = commit_counts.reset_index()
df.columns = ['date', 'commits']
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df = df.resample('D').sum().fillna(0)

#only keep last month of data
today = datetime.utcnow().date()
one_month_ago = today - timedelta(days=30)
df = df.loc[one_month_ago:today]

# Prepare data for grid layout
# Fill missing days
all_days = pd.date_range(start=one_month_ago, end=today)
df = df.reindex(all_days, fill_value=0)

# Reshape data into weekly grid
n_days = len(df)
n_cols = 7  # 7 days a week
n_rows = int(np.ceil(n_days / n_cols))

# Pad with NaNs if necessary to fill the grid
pad_size = n_cols * n_rows - n_days
commit_values = np.append(df['commits'].values, [np.nan] * pad_size)
grid_data = commit_values.reshape(n_rows, n_cols)

# Custom blue gradient colormap
colors = ["#f0f8ff", "#add8e6", "#4682b4", "#003366"]
cmap = LinearSegmentedColormap.from_list("custom_blues", colors)

# Ensure output directory exists
os.makedirs('assets', exist_ok=True)

# Plot grid heatmap
plt.figure(figsize=(12, n_rows * 0.6))
sns.heatmap(
    grid_data, 
    cmap=cmap, 
    cbar=True, 
    linewidths=0.5, 
    linecolor='white', 
    square=True,
    cbar_kws={'label': 'Commits per Day'}
)

# Remove axes and ticks
plt.xticks([])
plt.yticks([])
plt.title(f"{username}'s Commit Activity (Last 30 Days)", fontsize=14)
plt.tight_layout()
plt.savefig('assets/heatmap.png', transparent=True)
plt.close()

print("Blue gradient commit heatmap with legend generated successfully.")
