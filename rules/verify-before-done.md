# Verify before done

Apply the `verification-before-completion` skill whenever you are about to say
work is done, fixed, or passing. The user does not have to type
`/verification-before-completion`. `boss` already demands this of delegated
work; this rule covers everything else, including small changes the lead makes
itself.

**Invoke `Skill(verification-before-completion)` before** any of these:

- telling the user a change works, a bug is fixed, or tests/build/lint pass
- committing, pushing, or opening a PR (`ship`)
- marking a task complete or moving on to the next one
- accepting a subagent's report

The rule in one line: no claim without a command you ran **in this turn** whose
output proves it. If you did not run it, say what you did not verify instead.

**Skip when:**

- the request is a question, an explanation, or a read-only investigation
- nothing was changed (pure reading or planning)

Report in Thai, per `skills-explain-in-thai.md`: the command, the result, and
anything left unverified.
