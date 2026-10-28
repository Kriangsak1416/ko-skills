# Branch before work

Never write code on the integration or production branch. Before the **first
edit** of any code change in a git repository — a feature, a bug fix, a
refactor, even a one-line change — check where HEAD is:

```
git rev-parse --abbrev-ref HEAD
```

- **On `dev`, `develop`, `main`, `master`, or a release branch `v.X.Y.Z`:**
  invoke `Skill(ship)` and run Flow A step 1 to cut a feature branch first.
  Only then start the work.
- **On a feature branch (`#<n>_<slug>` / `feature/#<n>_<slug>`) for this same
  task:** keep working on it.
- **On a feature branch for a different task:** ask once whether to continue
  there or cut a fresh branch off dev.

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
