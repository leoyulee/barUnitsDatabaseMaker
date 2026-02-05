# Environment Setup
# Prereq
- Python 3
- Local repo of Beyond-All-Reason development
# Directions
1. Create `settings.json` by copying `.vscode/settings.json.template` and renaming it to `.vscode/settings.json`.
2. Within `settings.json`, set `debug.BAR-Path` to be the path of a local directory of the Beyond-All-Reason repo.
	- Clone it here: https://github.com/beyond-all-reason/Beyond-All-Reason

# How to create sqlite file
- Run `py UnitParser.py <path-to-local-BAR-dev-repo>`
	- Add `--resetDB` afterwards if you want to create a fresh sqlite file
