from github import Github # type: ignore
import pandas as pd # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.colors import LinearSegmentedColormap # type: ignore
import matplotlib.dates as mdates #type: ignore
from datetime import datetime, timedelta
import os

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


# Customise This section for Heatmap Aesthetics


colors = ["#f9f9f9", "#d0d0d0", "#909090", "#505050", "#101010"]
cmap = LinearSegmentedColormap.from_list("custom_greyscale", colors)

# Ensure output directory exists
os.makedirs('assets', exist_ok=True)

# Plot heatmap
plt.figure(figsize=(14, 1.5))
sns.heatmap(
    df.T, 
    cmap=cmap, 
    cbar=False, 
    linewidths=0.5, 
    linecolor='blue', 
    square=True
)
plt.axis('off')
plt.tight_layout()
plt.savefig('assets/heatmap.png', transparent=True)
plt.close()
print("main.py Executed Successfully")
