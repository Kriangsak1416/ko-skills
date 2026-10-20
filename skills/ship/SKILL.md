---
name: ship
description: This team's git workflow — branch off the repo's integration branch (dev/develop) as `[feature/]#<n>_<slug>`, commit in Thai and push, then cut a `v.X.Y.Z` release branch, finish the release git-flow style, and open a pull request from dev to main for someone else to approve. Use whenever the user starts a feature branch, wants finished work committed and pushed, cuts a version, or ships to production — "อัพงาน", "ขึ้น PRD", "ทำ release", "เปิด PR", "commit ให้หน่อย". Also use BEFORE the first edit of any code change (feature, bug fix, refactor — "เพิ่มฟีเจอร์", "แก้บั๊ก", "เริ่มงานใหม่") while HEAD is on dev/develop/main, to cut the feature branch first, and before any commit that would land on dev/develop/main.
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

## Match the repo, not these examples

The branch names below are **examples**. Every repo names things a little
differently and the repo always wins. Before the first command, look:

```
git branch -a --format='%(refname:short)'
git tag --list 'v.*' --sort=-v:refname | head
git log --merges --format='%h %s' -8 origin/main
```

Read three things off that output — getting any of them wrong produces a branch
or a message that does not match its neighbours:

- **The integration branch** — `dev` or `develop`. This document says `dev`;
  substitute whatever the repo actually has.
- **The feature-branch prefix** — bare `#<n>_<slug>` or `feature/#<n>_<slug>`.
  Take it from the existing branches, and number from the highest `#N` there,
  remote branches included — the local list is usually missing some.
- **The merge-message wording** — `git log --merges` on main shows the exact
  Thai phrasing previous releases used. Reuse it verbatim with the new numbers.

Say in one line which conventions you found before starting.

Recorded from `sv-api` (the Lumen API repo), verified on the v.1.10.10 release:
integration branch is **`develop`**, feature branches are
**`feature/#<n>_<slug>`**, feature merges into the release branch are worded
`รวม feature/#56_icu_bed_occupancy_bedtype เข้า release v.1.10.10`, and `main`
is **not protected** — the step-4 push to main succeeds, so step 5's PR is
purely the release record. An old `release/v.1.6.0` branch still sits on origin
from a retired convention; do not copy it.

## Flow A — feature work

### 1. Branch off dev

This step runs **before any code is written** — not when the user asks to
commit. Being asked to build a feature or fix a bug is the trigger; the user
will not say "แตก branch". Check where you are first:

```
git rev-parse --abbrev-ref HEAD
git status --porcelain
```

- On a feature branch for this task → skip to step 2.
- On dev/develop/main with a clean tree → run the commands below.
- On dev/develop with uncommitted changes that are **this task's work** (the
  code was started before branching) → `git switch -c '<branch>'` right where
  you are; the changes carry over. Do not stash, reset, or pull first. Say that
  the branch starts from local dev, which was not pulled.
- Uncommitted changes that are **not** this task's work → stop and report.

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

Check the branch before staging anything:

```
git rev-parse --abbrev-ref HEAD
```

If it prints `dev`, `develop`, `main` or `master`, **do not commit here.** Cut
the feature branch first as in step 1 (`git switch -c '#<n>_<slug>'` — the
uncommitted changes come along), then commit on it. Commits reach dev only
through Flow B's release merge, never directly.

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

### 0. Ask about QA first

The `qa-before-prd` rule applies to every Flow B run: before cutting anything,
ask once whether to run the `qa` audit. A **NO-GO verdict stops the release** —
report the blockers, do not cut the release branch.

`เลย` authorizes the release steps so you do not stop mid-flow for permission; it
is not an answer to whether the system gets tested first. Ask once, up front.

### 1. Decide the version

```
git tag --list 'v.*' --sort=-v:refname
```

Format is `v.MAJOR.MINOR.PATCH` — note the dot after `v`, matching the team's
existing tags. Ask the user which part bumps unless they already said. Look at
what size bump comparable work got last time and lead with that as the
recommendation, so the question is one click rather than a research task.

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
git merge --no-ff '#1_add_text_builder' -m 'รวม #1_add_text_builder เข้า release v.1.0.0'
git merge --no-ff '#2_fix_export_encoding' -m 'รวม #2_fix_export_encoding เข้า release v.1.0.0'
git push -u origin 'v.1.0.0'
```

Pass `-m` rather than accepting git's default `Merge branch ...` message — the
release history is read in Thai, and the wording to copy is whatever
`git log --merges` showed in the conventions check.

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

Requires the GitHub CLI. Run `gh auth status` first. If `gh` is missing or not
logged in, **install and log in yourself — do not hand the user a command to run.**

Install (Windows; on macOS use `brew install gh`):

```
winget install --id GitHub.cli --accept-source-agreements --accept-package-agreements
```

The current shell does not pick up the new PATH, so for the rest of this session
call it as `"C:\Program Files\GitHub CLI\gh.exe"` if bare `gh` is still not found.

Log in with the browser device flow. It needs no keyboard input, so it works from
the Bash tool — run it in the background with a long timeout, because it blocks
until the user finishes in the browser:

```
gh auth login --hostname github.com --git-protocol https --web
```

The output prints a one-time code (`XXXX-XXXX`) and the URL
`https://github.com/login/device`. Relay both to the user immediately, then wait
for the command to exit. Confirm with `gh auth status` before continuing; if it
still fails, stop and report — do not fall back to `--with-token` or ask the user
to paste a token into the chat.

Title — version, then date:

```
v.1.0.0 - 2026-08-01
```

Body — fill in `references/pr-template.md`. Write it to a temp file and pass
`--body-file`; Thai text with newlines through shell quoting is fragile.

**Step 5 is not optional and it is not a separate errand.** "อัพขึ้น PRD เลย"
means the release ends with a PR open — walking away after the tag and waiting to
be asked for the PR is an unfinished job.

**`เลย` is the yes.** When the instruction carries it — "อัพขึ้น PRD เลย",
"ทำ release เลย" — write the body and run `gh pr create`, then show the title and
body in the reply after the fact. Do not stop mid-flow to ask permission for a
step the user already ordered. Without `เลย`, show the title and body and get a
yes first; creating the PR notifies reviewers.

**Open the PR even when `git push origin main` succeeded.** On a repo where main
is not protected, the release is already on main by the time step 5 runs, so the
PR shows zero changed files — that is correct, not a reason to skip it. It is the
team's release record. Say so in the first line of the body, with the merge
commit and tag, so the reviewer is not left wondering why the diff is empty.

```
gh pr create --base main --head dev --title 'v.1.0.0 - 2026-08-01' --body-file <path>
```

If the user refuses the install or the login, print the filled title and body
for them to paste, plus the compare link:
`https://github.com/<owner>/<repo>/compare/main...dev?expand=1`

Report the PR URL when it is created. **Do not merge it** — someone else
approves and merges.

## Standing rules

- **Never commit directly to dev/develop/main/master.** Feature work lives on a
  feature branch; dev and main change only through Flow B's merges.
- **Never force-push and never rewrite published history.** No `--force`, no
  `rebase` on a branch that is already on origin, no amending a pushed commit.
- **Never merge or approve the PR yourself.**
- **Report honestly.** If tests fail, say so with the output and stop. If a
  change has no tests, write that in the PR instead of implying coverage.
- **Confirm before anything outward-facing** beyond the pushes this flow
  requires: no deploy, no release publish, no tag on someone else's commit.
- **Stop on divergence.** Local dev or main ahead of origin, an unexpected
  detached HEAD, or a dirty tree at the start of a flow means report, not repair.
