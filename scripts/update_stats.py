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

import json
from collections import defaultdict

language_stats = defaultdict(lambda: {"loc": 0, "repos": 0})

for repo in repos:

    repo_path = os.path.join(workspace, repo["name"])

    print(f"Analyzing {repo['name']}...")

    try:

        output = subprocess.check_output(
            [
                "tokei",
                repo_path,
                "--output",
                "json"
            ],
            text=True
        )

        data = json.loads(output)

        counted_languages = set()

        for language, values in data.items():

            if language == "Total":
                continue

            code = values.get("code", 0)

            language_stats[language]["loc"] += code

            if language not in counted_languages:
                language_stats[language]["repos"] += 1
                counted_languages.add(language)

    except Exception as e:

        print("Error:", repo["name"], e)

print(language_stats)
