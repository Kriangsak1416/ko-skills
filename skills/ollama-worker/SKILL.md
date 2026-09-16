---
name: ollama-worker
description: Hand small, self-contained web-dev chores to a free local Ollama model (e.g. qwen2.5-coder on a LAN box) instead of spending Claude tokens — an HTML fragment, a CSS class, a Tailwind component, a small JS/TS function, sample data, boilerplate. Claude stays the lead — writes a tight brief, calls the API, reads the result, verifies it. On first use it asks whether this machine should use an Ollama worker at all and where it lives. Use when the user says "ให้ ollama ทำ", "ใช้ qwen", "โยนให้ worker", "ใช้ local model", "ประหยัด token", or when a task is pure boilerplate a small coder model can do.
---

# Ollama worker — a free local coder for small web chores

A small model on the LAN. It is fast enough (~15 tok/s for a 3B model), free,
and good at one thing: producing a small, well-specified piece of web code. It
cannot see the repo, cannot run tools, and drifts on anything vague. **You
remain the lead**: you decide, you brief, you verify, you integrate. The
worker only types.

## First use on a machine — ask before using it

Not everyone who installs this skill has an Ollama server. The answer lives in
`~/.claude/ollama-worker.json`. **Before the first call in a session, read
that file:**

- **File missing** → ask the user, in Thai, with AskUserQuestion:

  > จะใช้ Ollama worker (โมเดล local ฟรี) ช่วยทำงานเว็บชิ้นเล็ก ๆ ไหม?
  > - **ใช้** — ถามต่อว่า host (เช่น `http://10.0.1.108:11434`) และ model (เช่น `qwen2.5-coder:3b`)
  > - **ไม่ใช้** — Claude ทำเองทั้งหมด จะไม่ถามอีก

  Then write the file and continue:

  ```json
  {"enabled": true, "host": "http://10.0.1.108:11434", "model": "qwen2.5-coder:3b"}
  ```
  or `{"enabled": false}`.

- **`enabled: false`** → this skill does nothing. Do the task yourself and
  do not mention the worker unless the user brings it up.
- **`enabled: true`** → use `host` and `model` from the file for every call.
  Never hard-code a host in a task; another machine has another server.

Verify the server once per session before the first real task:

```bash
curl -s --max-time 5 "$HOST/api/tags"
```

If it is unreachable or the model is not in the list, tell the user and fall
back to doing the task yourself — do not retry in a loop, and do not silently
flip `enabled` to false; that is the user's call.

## When to use it — and when not to

| Send to the worker | Keep for yourself / Sonnet |
|---|---|
| One HTML fragment, one CSS class, one Tailwind component | Anything spanning more than one file |
| A pure function ≤ ~60 lines with a clear signature | Logic that depends on repo conventions it cannot see |
| Sample/mock data, fixtures, lorem content | Bug hunts, refactors, anything needing judgment |
| Boilerplate: form markup, table markup, a fetch wrapper | Security-sensitive code (auth, SQL, file paths) |
| Translating a snippet between CSS ↔ Tailwind, JS ↔ TS | Anything where a wrong answer is expensive to spot |

Rule of thumb: if writing the brief takes longer than writing the code, write
the code.

## Calling it

Plain HTTP, no script needed. Non-streaming `/api/chat` with a system prompt
that pins the output shape:

```bash
curl -s --max-time 300 "$HOST/api/chat" -d '{
  "model": "'"$MODEL"'",
  "stream": false,
  "options": {"temperature": 0.2, "num_ctx": 16384},
  "messages": [
    {"role": "system", "content": "You are a senior web developer working under a lead engineer. Reply with code only, in exactly one fenced code block. No explanations, no extra files, no HTML boilerplate (doctype/head/body) unless the task explicitly asks for a full page. Do exactly what the task says — nothing more."},
    {"role": "user", "content": "<the task>"}
  ]
}'
```

The reply is one JSON object; the code is in `.message.content` inside a
fenced block. Pull it out with whatever is on the machine — `python -c
"import sys,json;print(json.load(sys.stdin)['message']['content'])"`,
`node -e`, or `jq -r .message.content` — then strip the fences yourself
before writing it to a file. `eval_count` / `prompt_eval_count` /
`total_duration` (ns) in the same object tell you what it cost.

To give it existing code to match, paste that file into the user message
under a heading (`### src/components/Button.tsx` + a fenced block). Keep it to
one file; the context window is small and it dilutes the task.

Without the system prompt the model chats ("Certainly! …", an
`### Explanation` section) — verified. Always send it.

## The loop

1. **Brief tightly.** The model does what the words say, literally. Verified
   failure mode: asked for "a button", it returned a whole HTML page with
   `<!DOCTYPE>`, `<head>` and inline CSS. So state, in the task:
   - the exact output shape: "CSS only", "one `<form>` fragment, no page
     wrapper", "a single exported TypeScript function `slugify(s: string): string`"
   - names it must use: class names, function names, prop names, ids
   - what to leave out: "no comments", "no inline styles", "no framework"
   - the one file whose style it must match, if any
2. **Run it, write the extracted code to a path you chose** — a scratch file or
   the target file.
3. **Read the result yourself.** It is a claim, not code you can trust. Check
   names, check it does not include boilerplate you excluded, check it compiles
   or renders (run the project's lint/build/test as you would for any change).
4. **Fix small drift yourself; re-brief large drift.** A wrong class name is a
   one-line edit. If the shape is wrong, tighten the brief and run once more.
   After two misses, do the task yourself — the worker is not the right tool
   for that job.

## Standing rules

- **Never tell the user the worker's code works until you verified it.**
- **Never send secrets, credentials, or patient/personal data in a task or
  pasted context.** The server is a shared LAN box.
- The worker never writes to the repo on its own — only you do, at a path you
  chose, after reviewing. It cannot commit, push, or run anything.
- Under `boss`, the worker is one more crew member for the smallest chores; it
  does not replace `coder` for real implementation work.
- If the server runs a token-counting proxy (a dashboard on another port),
  put the proxy port in `host` so the user's dashboard sees the traffic.
