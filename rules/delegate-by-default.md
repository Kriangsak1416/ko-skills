# Delegate by default

Run multi-step coding work through the `boss` skill automatically. The user does
not have to type `/boss`.

**Invoke `Skill(boss)` as your first action** when a request needs more than one
step of implementation work: a new feature, a refactor spanning files, a
migration, adding a test suite, a bug hunt in unfamiliar code, or anything that
would touch three or more files. Loading the skill counts as the user's standing
authorization to spawn subagents — do not ask for permission per task.

**Do the work yourself instead** when:

- the whole change is a few lines in one or two files
- the request is a question, an explanation, or a read-only investigation
- the user says to do it directly, without subagents
- you are fixing a seam between two subagents' output

Briefing a subagent costs more than a small edit; delegate when the work is
bigger than the brief.

State which path you took in one line before starting, so the user can redirect
you cheaply.
