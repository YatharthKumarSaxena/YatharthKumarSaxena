import os
import shutil
import subprocess
import tempfile
import requests

IGNORE_LANGUAGES = {
    "JSON",
    "YAML",
    "TOML",
    "Dockerfile",
    "Makefile",
    "C Header",
    "Pug",
    "Jupyter Notebooks",
    "Markdown",
    "Text",
    "INI",
    "XML",
    "CSV",
    "Batch",
}
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
        
            if language in IGNORE_LANGUAGES:
                continue
        
            code = values.get("code", 0)
        
            if code == 0:
                continue
        
            language_stats[language]["loc"] += code
        
            if language not in counted_languages:
                language_stats[language]["repos"] += 1
                counted_languages.add(language)

    except Exception as e:

        print("Error:", repo["name"], e)

# ---------- Update README ----------

sorted_stats = sorted(
    language_stats.items(),
    key=lambda x: x[1]["loc"],
    reverse=True
)

table = "📦 Repository Statistics\n\n"
table += f"{'Language':<18}{'Repos':>8}{'LOC':>12}\n"
table += "-" * 40 + "\n"

total_loc = 0
total_repos = len(repos)

for language, values in sorted_stats:

    if values["loc"] == 0:
        continue

    total_loc += values["loc"]

    table += (
        f"{language:<18}"
        f"{values['repos']:>8}"
        f"{values['loc']:>12,}\n"
    )

table += "-" * 40 + "\n"
table += (
    f"{'TOTAL':<18}"
    f"{total_repos:>8}"
    f"{total_loc:>12,}\n"
)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

start = "<!--START_SECTION:code_stats-->"
end = "<!--END_SECTION:code_stats-->"

new_section = (
    start
    + "\n\n```text\n"
    + table
    + "```\n\n"
    + end
)

import re

pattern = re.compile(
    rf"{re.escape(start)}.*?{re.escape(end)}",
    flags=re.S,
)

updated = pattern.sub(new_section, readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)

print("README updated successfully!")
