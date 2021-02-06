#!/bin/bash
HOOK_NAMES="applypatch-msg pre-applypatch post-applypatch pre-commit prepare-commit-msg commit-msg post-commit pre-rebase post-checkout post-merge pre-receive update post-receive post-update pre-auto-gc"
# assuming the script is in a script directory, one level into the repo
HOOK_DIR=$(git rev-parse --show-toplevel)/.git/hooks
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

for hook in ${HOOK_NAMES}; do
    [[ ! -f "${SCRIPT_DIR}/${hook}" ]] && continue

    # If the hook already exists, is executable, and is not a symlink
    if [ ! -h "${HOOK_DIR}/${hook}" ] && [ -x "${HOOK_DIR}/${hook}" ]; then
        mv "${HOOK_DIR}/${hook}" "${HOOK_DIR}/${hook}.local"
    fi
    # create the symlink, overwriting the file if it exists
    # probably the only way this would happen is if you're using an old version of git
    # -- back when the sample hooks were not executable, instead of being named ____.sample
    ln -s -f "${SCRIPT_DIR}/${hook}" "${HOOK_DIR}/${hook}"
done
