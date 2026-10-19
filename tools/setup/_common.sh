#!/usr/bin/env bash
# Shared helpers for scenario setup scripts.
# Each tools/setup/sNN.sh builds the scenario's starting branches from the
# module branch (or main) and force-pushes them, so re-running = reset.
# Local dry run:  NO_PUSH=1 bash tools/setup/s04.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
MODEL="Contoso.SemanticModel/definition"
SALES="$MODEL/tables/Sales.tmdl"
PRODUCT="$MODEL/tables/Product.tmdl"
PUSH_BRANCHES=()

# Snapshot the tooling first: checking out scenario branches swaps the working
# tree, and those branches may carry an older copy of tools/.
TOOLS_SNAPSHOT="$(mktemp -d)"
cp "$ROOT/tools/tmdl.py" "$TOOLS_SNAPSHOT/"
tmdl() { python3 "$TOOLS_SNAPSHOT/tmdl.py" "$@"; }

# commit_as "<name>" "<message>"  - fictional teammates make log/blame readable
commit_as() {
  local who="$1" msg="$2" email
  email="$(echo "$who" | tr '[:upper:] ' '[:lower:]-')@example.com"
  git add -A -- "Contoso.*"   # only model files - never stray local files
  for f in .gitignore CHANGELOG.md; do [[ -e "$f" ]] && git add -- "$f"; done
  git -c user.name="$who" -c user.email="$email" commit -q -m "$msg"
}

ref_exists() { git rev-parse --verify -q "$1" >/dev/null; }

# start_from <module-branch>: sets $BASE to where the scenario starts.
# (Sets a variable instead of echoing, so PUSH_BRANCHES survives - no subshell.)
start_from() {
  local mod="$1"
  for r in "origin/$mod" "$mod"; do ref_exists "$r" && { BASE="$r"; return; }; done
  # module branch doesn't exist yet -> create it from main and push it once
  local main=main; ref_exists origin/main && main=origin/main
  git branch -q "$mod" "$main"
  PUSH_BRANCHES+=("$mod")
  BASE="$mod"
}

# branch <name> <from>: (re)create a scenario branch and switch to it
branch() {
  git checkout -q -B "$1" "$2"
  PUSH_BRANCHES+=("$1")
}

finish() {
  git checkout -q "${ORIGINAL_BRANCH:-main}" 2>/dev/null || true
  echo "Created/reset branches: ${PUSH_BRANCHES[*]}"
  if [[ -z "${NO_PUSH:-}" ]]; then
    git push --force origin "${PUSH_BRANCHES[@]}"
  fi
}

ORIGINAL_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
