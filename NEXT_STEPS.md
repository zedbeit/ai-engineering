# Next steps: M0 week 3 (handoff, updated 2026-11-22)

Curriculum: `/Users/deehaz/Downloads/AI_Engineering_Curriculum.html` (M0 · Python for AI engineering, weeks 1–3).

M0 "Done when": all CS50P problem sets done by hand, and P0 on GitHub with green CI, tests written before the code, and an AI-tooling log.

## Where M0 stands

| Deliverable | State |
|---|---|
| Expense tracker (`expense-tracker/`) | Done |
| Async fan-out (`async-fanout/`) | Done |
| FastAPI intake service, P0 (`intake-service/`) | Done |
| pandas notebook (`notebooks/`) | Done |
| CS50P problem sets 0–9, by hand | Done |
| Anthropic Academy "Claude Code 101" + "Claude Code in Action" | Done |
| CS146S week 1: Claude Code trace dissection write-up (`trace-dissection/README.md`) | Done 2026-11-22, except section 7 (comparison with Ahmed) |
| **CS146S week 4: `AGENTS.md` for an unfamiliar open-source repo** | **Next** |

## Now

1. **CS146S week 4: write an `AGENTS.md` for an unfamiliar open-source repo**, making it agent-ready. Pick the repo first.
2. **Trace dissection, loose ends:**
   - Section 7 of `trace-dissection/README.md` (comparison with Ahmed) is still `TODO`: fill it in after comparing runs, or remove it.
   - `trace-dissection/` is not committed yet.
   - Sections 1–4 and the analysis were drafted by Claude; sections 5–6 were chosen by me and written up by Claude at my request (all in `trace-dissection/AI_TOOLING_LOG.md`). Method notes: `~/Documents/agentic coding/tracing-claude-code.md`.

Assignments: https://github.com/mihail911/modern-software-dev-assignments

## What the intake service has (for reference)

- `SPEC.md` with a Goals section; 55 tests (written before the code); `AGENTS.md` and `CLAUDE.md`.
- `.claude/settings.json`: a pytest hook after every `.py` edit, and a deny rule on editing `tests/` and `SPEC.md`.
- `.claude/agents/verifier.md`: a read-only subagent that checks the code against `SPEC.md` with evidence (a requirement table, deliberate bugs planted in a copy, real requests, a verdict per goal).
- `Dockerfile`, plus `.github/workflows/intake-service.yml` at the repo root: ruff, mypy and pytest, then build the image and send it real requests.
- The workflow loop: goals → spec → automatic checks (hook) → implement → independent verifier → my acceptance.

## After M0: M1 / P1 document intelligence (weeks 4–6)

Add `POST /documents/{id}/extract` to the intake service: an LLM turns the document into JSON, validated by Pydantic, with a retry when validation fails. Golden set of 50 hand-labelled documents; field-level accuracy across 3 models, with $ per 1,000 docs; a deployed endpoint. Main course: Anthropic Academy "Building with the Claude API".

## CS146S notes

- No public videos; Fall 2026 slides are gated. Public material is the readings per week and the 2025 slides.
- Syllabus: https://themodernsoftware.dev ("Syllabus" tab, Fall 2026). Week 2 is spec-driven development; week 4 is `CLAUDE.md`, `AGENTS.md` and hooks; week 5 is agent-ready codebases. Week 3 (skills) returns in M4.
- Other week 4 material: https://docs.factory.com/harness/agents-md and Boris Cherny's 2025 slides, https://docs.google.com/presentation/d/1bv7Zozn6z45CAh-IyX99dMPMyXCHC7zj95UfwErBYQ8/edit?usp=sharing
- Week 5 video, Making Codebases Agent Ready: https://www.youtube.com/watch?v=ShuJ_CN6zr4

## Environment notes

- Each project folder is its own uv project with its own `.venv`. Run `uv run ...` from inside the project folder, and open that folder in its own VS Code window.
- Docker Desktop must be running for `docker build` (`open -a Docker`).
- Claude Code's safety check blocks `git push` unless that message asks for the push.
