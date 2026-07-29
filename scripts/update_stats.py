import subprocess
import re

# Run tokei on all cloned repositories
output = subprocess.check_output(
    ["tokei", "repos"],
    text=True
)

lines = output.splitlines()

stats = []

for line in lines:
    line = line.strip()

    # Skip headers and separators
    if (
        line.startswith("Language")
        or line.startswith("-")
        or line.startswith("=")
        or line == ""
        or line.startswith("Total")
    ):
        continue

    parts = re.split(r"\s+", line)

    # Expected format:
    # Language Files Lines Code Comments Blanks
    if len(parts) >= 6:
        language = parts[0]
        files = parts[1]
        code = parts[3]

        # Ignore Markdown and Text
        if language in ["Markdown", "Text"]:
            continue

        stats.append((language, files, code))

# Build README section
table = "📦 Repository Statistics\n\n"
table += "Language           Files      LOC\n"
table += "────────────────────────────────────\n"

for lang, files, loc in stats:
    table += f"{lang:<16}{files:>6}{loc:>10}\n"

# Replace README section
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = re.compile(
    r"<!--START_SECTION:code_stats-->.*?<!--END_SECTION:code_stats-->",
    re.DOTALL,
)

replacement = (
    "<!--START_SECTION:code_stats-->\n\n"
    "```text\n"
    + table +
    "\n```\n\n"
    "<!--END_SECTION:code_stats-->"
)

updated = pattern.sub(replacement, readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)

print("README updated successfully.")
