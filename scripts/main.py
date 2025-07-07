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
#df = df.resample('D').sum().fillna(0)

# Only keep last 28 days
today = datetime.utcnow().date()
days_ago_28 = today - timedelta(days=27)
df = df.resample('D').sum().fillna(0)
df = df.loc[days_ago_28:today]

# Prepare data for grid layout
all_days = pd.date_range(start=days_ago_28, end=today)
df = df.reindex(all_days, fill_value=0)

# Reshape data into 4x7 grid (4 weeks, 7 days per week)
commit_values = df['commits'].values
grid_data = commit_values.reshape(4, 7)

# Custom blue gradient colormap for dark mode
colors = [ "#103092","#0074D9", "#0B9CD1", "#1F9FF4"]
cmap = LinearSegmentedColormap.from_list("custom_blues_dark", colors)

# Ensure output directory exists
os.makedirs('assets', exist_ok=True)

# Dark background setup
plt.style.use('dark_background')

# Plot heatmap
plt.figure(figsize=(10, 2.5))
sns.heatmap(
    grid_data, 
    cmap=cmap, 
    cbar=False, 
    linewidths=0.5, 
    linecolor='black', 
    square=True,
    #cbar_kws={'label': 'Commits per Day'}
)

# Remove axes and ticks
plt.xticks([])
plt.yticks([])
plt.title("")
plt.tight_layout()
plt.savefig('assets/heatmap.png', transparent=True)
plt.close()

print("main.py executed successfully.")