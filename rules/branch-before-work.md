# Branch before work

Never write code on the integration or production branch. Before the **first
edit** of any code change in a git repository — a feature, a bug fix, a
refactor, even a one-line change — check where HEAD is:

```
git rev-parse --abbrev-ref HEAD
```

**One feature branch carries every task until it goes to PRD.** A new request
does not get a new branch while the current one is still unreleased; a branch
that has already shipped is never reused. Features reach dev only through
Flow B's release merge, so "already on dev" means "already in PRD". After
`git fetch origin`, a feature branch is **unreleased** when any of these holds:

- it has commits dev does not: `git rev-list --count 'origin/dev..<branch>'` > 0
- it is the current branch and has uncommitted changes
- its tip is exactly `origin/dev` — cut, nothing done on it yet

Then:

- **On a feature branch (`#<n>_<slug>` / `feature/#<n>_<slug>`) that is
  unreleased:** keep working on it — even when the new request is a different
  task. Do not ask.
- **On a feature branch that is already released:** invoke `Skill(ship)` and
  run Flow A step 1 to cut a fresh branch off dev.
- **On `dev`, `develop`, `main`, `master`, or a release branch `v.X.Y.Z`:**
  look for an unreleased local feature branch —
  `git branch --no-merged origin/dev --format='%(refname:short)'`, keeping only
  names with `#`. One found → `git switch '<branch>'` and work there. Several →
  ask once which. None → invoke `Skill(ship)` and run Flow A step 1 to cut a
  feature branch. Only then start the work.

This runs **before** `boss` or any delegation: the lead cuts the branch, the
subagents work inside it. State the branch in one line next to the
delegate-by-default line, so the user can redirect cheaply.

**The same check runs before every commit.** If HEAD is on dev/develop/main/
master, do not commit — cut the feature branch (`git switch -c`, uncommitted
changes carry over) and commit there. Commits reach dev only through Flow B's
release merge.

**Skip when:**

- the folder is not a git repository
- the user says to work on the current branch — "ทำบน dev เลย", "ไม่ต้องแตก branch"
- the request is a question, an explanation, or a read-only investigation
- the repo has no `dev`/`develop` — ask once per session whether to branch off
  `main` or work on it directly, then follow the answer
