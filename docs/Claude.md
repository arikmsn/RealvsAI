# Claude Instructions for RealVsAI

## Project Links
- Git repo: https://github.com/arikmsn/realvsai
- PRD: docs/PRD.md
- Tech Spec: docs/TechSpec.md
- Status: docs/Status.md

## General Rules
1. Keep the code as clean, readable, and simple as possible.
2. Any temporary or experimental files must go into the `tmp/` folder only. That folder is ignored by git.
3. If there is unused or “orphaned” code, delete it instead of leaving it commented out.
4. If the same logic is used more than once, extract it into a shared function/module and reuse it.
5. After every meaningful code change, update `docs/Status.md` and explain:
   - What changed
   - Why it changed
   - What is still left to do
6. Whenever I correct you on something important about this project, update this file under **Lessons Learned**.

## Workflow Rules
1. Before changing code:
   - Read `Claude.md`.
   - Read `Status.md` to understand the current state.
   - If needed, read `PRD.md` and `TechSpec.md` for context.
2. All temporary scripts, scratch files, and debug experiments live in `tmp/` only.
3. Never bypass safety hooks or code review.

## Lessons Learned
- This section will be updated during the project as I correct you.
