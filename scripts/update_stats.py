import os
import shutil
import subprocess
import tempfile
import requests

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

repos = []

page = 1

while True:
    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        f"?per_page=100&page={page}&sort=updated"
    )

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    data = r.json()

    if not data:
        break

    repos.extend(data)
    page += 1

print(f"Found {len(repos)} repositories.")

workspace = tempfile.mkdtemp(prefix="loc_stats_")

print("Workspace:", workspace)

for repo in repos:

    name = repo["name"]

    clone_url = (
        f"https://x-access-token:{TOKEN}"
        f"@github.com/{USERNAME}/{name}.git"
    )

    target = os.path.join(workspace, name)

    print("Cloning", name)

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            clone_url,
            target
        ],
        check=True
    )

print("All repositories cloned successfully.")
