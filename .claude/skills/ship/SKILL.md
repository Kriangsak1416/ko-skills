---
name: ship
description: This team's git workflow — branch off dev as `#<n>_<slug>`, commit in Thai and push, then cut a `v.X.Y.Z` release branch, finish the release git-flow style, and open a pull request from dev to main for someone else to approve. Use whenever the user starts a feature branch, wants finished work committed and pushed, cuts a version, or ships to production — "อัพงาน", "ขึ้น PRD", "ทำ release", "เปิด PR", "commit ให้หน่อย".
---

# Ship — feature branch → release → PR

Two flows. **Flow A** is day-to-day feature work. **Flow B** runs when a version
goes to production (PRD). Commit messages and the PR description are written in
**Thai**; branch names and slugs stay in English.

## The `#` trap — read this before typing any command

Branch names always start with `#`, which is a comment character in PowerShell,
in bash, and in git commit messages. Three consequences, all verified:

- **Single-quote every branch name.** `git switch -c '#1_add_text_builder'`.
  Unquoted, PowerShell drops the argument silently — `git branch #1_x` just
  lists branches, exits 0, and creates nothing.
- **Commit with `--cleanup=whitespace`.** Without it, a repo or user config with
  `commit.cleanup=strip` reads the whole subject as a comment and aborts with
  `Aborting commit due to empty commit message`.
- **In GitHub URLs `#` is `%23`** — `.../compare/main...%231_add_text_builder`.

## Flow A — feature work

### 1. Branch off dev

```
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c '#1_add_text_builder'
```

Numbering: use the issue or ticket number when there is one. Otherwise take the
next number above the highest `#N` already in use —
`git branch -a --format='%(refname:short)'` — and say which number you picked.
The slug is lowercase English `snake_case`, 2–4 words, describing the feature.

Refuse to start from anything but an up-to-date `dev`. If `git pull --ff-only`
fails, dev has diverged locally — stop and report it rather than merging blindly.

### 2. Do the work

The implementation itself is normal work: if it is multi-step, the
delegate-by-default rule applies and the `boss` skill runs it. This skill owns
the git side only.

### 3. Commit

```
git status --porcelain
git add <the files you actually changed>
git commit --cleanup=whitespace -m '#1 เพิ่มตัวสร้างข้อความสำหรับหน้ารายงาน'
```

- Subject: `#<n> <สรุปสั้น ๆ ภาษาไทย>`, ไม่เกิน 72 ตัวอักษร — บอกว่า branch นี้ทำอะไร
- If the branch did several distinct things, add a body of Thai bullets
- Stage deliberately. Never `git add -A` when the working tree has files
  unrelated to this branch
- Check for secrets before staging: `.env`, keys, tokens, credentials, dumps
- Never write "ทดสอบผ่าน" in a message unless you ran the tests and saw them pass

One feature per branch. Several commits on the branch are fine.

### 4. Push

```
git push -u origin '#1_add_text_builder'
```

Report the branch name and what was committed. Stop here — Flow A does not open
a PR and does not touch dev.

## Flow B — release to PRD

### 1. Decide the version

```
git tag --list 'v.*' --sort=-v:refname
```

Format is `v.MAJOR.MINOR.PATCH` — note the dot after `v`, matching the team's
existing tags. Ask the user which part bumps unless they already said.

### 2. Cut the release branch from dev

The branch is named for the version with no prefix — `v.1.0.0`, not
`release/v.1.0.0`.

```
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c 'v.1.0.0'
```

The tag created in step 4 uses that same name, and git warns
`refname 'v.1.0.0' is ambiguous` on every command while both refs exist. Step 4
therefore deletes the branch **before** creating the tag. Never leave the two
alive together.

### 3. Merge in the features for this version

Only the branches the user names — not everything that exists.

```
git merge --no-ff '#1_add_text_builder'
git merge --no-ff '#2_fix_export_encoding'
git push -u origin 'v.1.0.0'
```

Run the full test suite here. This is the last checkpoint before main. On a
merge conflict that is not trivially obvious, stop and ask — do not guess whose
change wins.

### 4. Finish the release (git-flow standard)

Merge into main, merge back into dev, **delete the branch, then tag** — in that
order, so the branch and the tag never share the name at the same time.

```
git switch main
git pull --ff-only origin main
git merge --no-ff 'v.1.0.0' -m 'รวม release v.1.0.0'
git switch dev
git merge --no-ff 'v.1.0.0' -m 'รวม release v.1.0.0 กลับเข้า dev'
git push origin dev
git branch -d 'v.1.0.0'
git push origin --delete 'v.1.0.0'
git switch main
git tag -a 'v.1.0.0' -m 'v.1.0.0 - 2026-08-01'
git push origin main --follow-tags
```

Take the date from the system (`Get-Date -Format 'yyyy-MM-dd'`), never from
memory.

**If `git push origin main` is rejected**, main is a protected branch that only
accepts an approved PR — which is the normal setup for this flow. Undo the local
merge and let the PR do the work:

```
git switch main
git reset --hard origin/main
git tag -d 'v.1.0.0'
```

dev already carries the release, so nothing is lost. Tell the user the tag is
pending, and create it after the PR is merged:

```
git fetch origin
git switch main
git pull --ff-only origin main
git tag -a 'v.1.0.0' -m 'v.1.0.0 - 2026-08-01'
git push origin 'v.1.0.0'
```

### 5. Open the pull request (dev → main)

Requires the GitHub CLI. Check `gh auth status` first; if `gh` is missing, tell
the user to run `winget install --id GitHub.cli` then `gh auth login`.

Title — version, then date:

```
v.1.0.0 - 2026-08-01
```

Body — fill in `references/pr-template.md`. Write it to a temp file and pass
`--body-file`; Thai text with newlines through shell quoting is fragile.

**Show the user the title and body, and get a yes, before creating the PR** —
creating it notifies reviewers.

```
gh pr create --base main --head dev --title 'v.1.0.0 - 2026-08-01' --body-file <path>
```

If the user would rather not install `gh`, print the filled title and body for
them to paste, plus the compare link:
`https://github.com/<owner>/<repo>/compare/main...dev?expand=1`

Report the PR URL when it is created. **Do not merge it** — someone else
approves and merges.

## Standing rules

- **Never force-push and never rewrite published history.** No `--force`, no
  `rebase` on a branch that is already on origin, no amending a pushed commit.
- **Never merge or approve the PR yourself.**
- **Report honestly.** If tests fail, say so with the output and stop. If a
  change has no tests, write that in the PR instead of implying coverage.
- **Confirm before anything outward-facing** beyond the pushes this flow
  requires: no deploy, no release publish, no tag on someone else's commit.
- **Stop on divergence.** Local dev or main ahead of origin, an unexpected
  detached HEAD, or a dirty tree at the start of a flow means report, not repair.
