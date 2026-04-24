#!/usr/bin/env bash
# Commit-scope guard — refuse `git commit` when the index contains files
# the agent did not explicitly list.
#
# Problem this solves (quality-checklist §12 violation, 2026-04-24):
#   An autonomous agent that does `git add path/to/one/file && git commit`
#   sweeps in any already-staged files the *user* had in the index,
#   silently attributing the user's in-progress work to the agent's
#   commit message. The resulting commit is non-destructive but
#   historically misleading and hard to audit.
#
# Usage:
#   scripts/git_guard_commit.sh --repo <path> \
#       <expected-path> [<expected-path> ...] -- \
#       <any git commit args>
#
# The `--repo` flag is REQUIRED because some shell environments auto-cd
# on subshell entry; relying on $PWD is unsafe. Pass an absolute path.
#
# Example:
#   scripts/git_guard_commit.sh --repo /home/ywatanabe/proj/scitex-orochi \
#       src/scitex_orochi/_cli/_help_availability.py -- \
#       -m "docs: translate help-display policy name to English"
#
# Behaviour:
#   1. Capture the explicit list of paths the agent intended to commit.
#   2. Compare against `git diff --staged --name-only`.
#   3. If the two sets differ, abort with a diff and exit 1.
#   4. Otherwise forward all post-`--` args to `git commit`.
#
# The script does not touch the working tree or the index. It is a
# guard, not a fixer — if the sets mismatch, the agent should unstage
# the extras (`git restore --staged <path>`) and re-run.
set -euo pipefail

die() {
    echo "git_guard_commit: $*" >&2
    exit 1
}

repo=""
if [[ "${1:-}" == "--repo" ]]; then
    repo="${2:-}"
    shift 2
    [[ -n "$repo" ]] || die "--repo requires a path argument"
    [[ -d "$repo/.git" ]] || die "--repo path is not a git repo: $repo"
else
    die "missing required --repo <path> flag (first arg)"
fi

expected=()
while [[ $# -gt 0 && "$1" != "--" ]]; do
    expected+=("$1")
    shift
done
[[ "${1:-}" == "--" ]] || die "missing '--' separator between path list and git-commit args"
shift

[[ ${#expected[@]} -gt 0 ]] || die "no expected paths given"

# Normalize both sets: sort, strip trailing whitespace, drop empties.
expected_sorted=$(printf '%s\n' "${expected[@]}" | LC_ALL=C sort -u)
staged_sorted=$(git -C "$repo" diff --staged --name-only | LC_ALL=C sort -u)

if [[ "$expected_sorted" != "$staged_sorted" ]]; then
    echo "GUARD FAIL — staged file set does not match expected." >&2
    echo >&2
    echo "Expected:" >&2
    echo "${expected_sorted//$'\n'/$'\n'  }" | sed '1s/^/  /' >&2
    echo >&2
    echo "Actually staged:" >&2
    echo "${staged_sorted//$'\n'/$'\n'  }" | sed '1s/^/  /' >&2
    echo >&2
    echo "Diff (expected vs staged, - = in expected only, + = staged only):" >&2
    diff <(echo "$expected_sorted") <(echo "$staged_sorted") | sed 's/^/  /' >&2 || true
    echo >&2
    echo "Fix: unstage extras with 'git restore --staged <path>' and re-run." >&2
    exit 1
fi

exec git -C "$repo" commit "$@"
