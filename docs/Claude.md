# Claude Instructions for RealVsAI

## Project Links
- Git repo: https://github.com/arikmsn/realvsai
- PRD: docs/PRD.md
- Tech Spec: docs/TechSpec.md
- Status: docs/Status.md

## Project Structure
```
docs/
  Claude.md      # This file - project instructions and house rules
  PRD.md         # Product Requirements Document (business context, user stories, metrics)
  TechSpec.md    # Technical design based on the PRD
  Status.md      # Current state: what exists, what changed, open bugs, next tasks
tmp/             # Temporary / experimental files (git-ignored)
```

## Before Writing Any Code
1. Read this file (`docs/Claude.md`).
2. Read `docs/Status.md` to understand the current state.
3. Use `docs/PRD.md` and `docs/TechSpec.md` as the single source of truth for product and technical decisions.
4. If something important is missing in PRD or TechSpec, **ask questions first** and update those docs before touching code.

## Code Quality Rules
1. Keep code as clean, readable, and simple as possible.
2. If the same logic is used more than once, extract a function or shared module and reuse it.
3. Remove dead or unused code instead of leaving large commented blocks.
4. Prefer clear logging over print statements.
5. After any meaningful change, update `docs/Status.md` with: what changed, why, and what's next.

## Git Rules
1. Never commit directly to `main`; use branches.
2. Commit frequently with clear messages.
3. The `tmp/` folder must never contain anything that should be committed.
4. All temporary scripts, scratch files, and debug experiments live in `tmp/` only.

## Multi-Agent Team Workflow

When a new feature or significant change is requested, the following virtual team reviews and refines requirements **before any code is written**:

| Role | Responsibility |
|------|---------------|
| **CEO** | Business vision, priorities, go/no-go decisions |
| **PM** | User stories, acceptance criteria, scope definition |
| **Growth PM** | Virality, retention hooks, growth metrics |
| **Frontend** | UI/UX feasibility, component design, performance |
| **Backend** | API design, data models, scalability |
| **AI Expert** | AI/ML pipeline, model selection, prompt engineering |
| **QA** | Test strategy, edge cases, quality gates |
| **Media** | Content strategy, assets, branding |

### Feature Request Flow
1. **Clarify** - The team asks clarifying questions and discusses trade-offs.
2. **Update PRD** - PM updates `docs/PRD.md` with finalized requirements.
3. **Update TechSpec** - Backend/Frontend/AI update `docs/TechSpec.md` with technical design.
4. **Confirm** - Wait for user confirmation of the spec.
5. **Implement** - Only now start writing code.
6. **Update Status** - At the end of each task, update `docs/Status.md`.

## Safety Rules
1. Never bypass safety hooks or code review.
2. Never commit secrets, API keys, or credentials.
3. If unsure about a decision, ask rather than guess.

## Lessons Learned
- This section will be updated during the project as corrections are made.
