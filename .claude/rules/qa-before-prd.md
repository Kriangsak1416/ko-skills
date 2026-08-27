# Ask about QA before a PRD build

Before the **first build/pack/deploy command of a production release**, ask the
user once whether to run the `qa` audit first. The user does not have to type
`/qa` — it is your job to offer it while it can still stop a bad release.

**Ask when** the request is a production build: "build ขึ้น PRD", "ขึ้น PRD",
"แพ็กขึ้นเซิร์ฟเวอร์", "ทำ release", `npm run pack`, an rsync to the web root,
or any Flow B run of the `ship` skill.

Ask with `AskUserQuestion`, one question, two options:

- **รัน QA ก่อน (แนะนำ)** — `Skill(qa)` ทั้งชุด: build readiness → bug audit →
  web security audit → migrations → GO / NO-GO
- **build เลย** — ข้าม QA, ผู้ใช้รับความเสี่ยงเอง

**On "รัน QA ก่อน":** invoke `Skill(qa)`, run it in full, and stop at the
GO / NO-GO verdict. **NO-GO means do not build** — report the blockers and wait.
On GO, continue straight into the build the user originally asked for.

**Skip the question when:**

- the user already said to skip it — "ไม่ต้อง QA", "ข้าม QA", "รีบ", "build เลย"
- `qa` already ran in this session and nothing has changed since its verdict
- the build is not for production — dev server, preview build, local test

**`เลย` does not skip this question.** "อัพขึ้น PRD เลย" authorizes the release
steps so you do not stop for permission mid-flow; it is not an answer to whether
the system should be tested first. Ask once, up front, then run the rest without
further prompting.

Ask **once per release**, before the first command — not between build steps.
