from github import Github # type: ignore
import pandas as pd # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
from datetime import datetime
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

# Plot heatmap
plt.figure(figsize=(14, 2))

# Customise This command for Heatmap Aesthetics
sns.heatmap(df.T,
            cmap = "Greys",
            cbar=False,
            linewidths = 0.5,
            linecolor = "white",
            square = True)


plt.title(f'{username}@GitHub')
plt.axis("off")
plt.tight_layout()
plt.savefig('assets/heatmap.png')
print("main.py Executed Successfully")
