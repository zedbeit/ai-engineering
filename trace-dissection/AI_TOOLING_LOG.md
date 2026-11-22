# AI tooling log: trace dissection

| Date | Tool | What AI did | What I did |
|---|---|---|---|
| 2026-11-18 | Claude Code | Broke the assignment into steps, picked the task, wrote the `README.md` skeleton and added `.claude-trace/` to `.gitignore` | TODO |
| 2026-11-18 | Claude Code | Diagnosed the claude-trace 404 (it ran a bundled Claude Code 1.0.128 because 2.1.327 is a compiled binary). Found that claude-code-logger always runs in chat mode and drops the system prompt, tools and token usage. Wrote `record-proxy.mjs` to save each request/response as raw JSON, without headers. Saved the first attempt's diff as `run1.diff` | Ran the sessions |
| 2026-11-18 | Claude Code | Wrote `summarize.py` (turns, tool calls, tokens per run). Found that the "plan mode" run never entered plan mode, renamed it `run2-normal-repeat`, and confirmed from the trace that the agent read the teaching-mode memory before editing `AI_TOOLING_LOG.md`. Saved the walkthrough to `~/Documents/agentic coding/tracing-claude-code.md` | Ran runs 1 and 2 |
| 2026-11-18 | Claude Code | Two interactive "plan mode" runs never entered plan mode; recorded the plan-mode run myself, headless (`claude -p --permission-mode plan`), into `run4-plan`; copied its plan to `run4-plan.md`; added the plan-mode findings to the tracing doc | Ran runs 1–3 interactively |
| 2026-11-22 | Claude Code | Explained how to read the recordings (summary columns, quota check, `max_tokens`, cache read/write, the cache lifetime, API-equivalent cost) and added them to the tracing doc | Asked the questions, read the recordings |
| 2026-11-22 | Claude Code | Filled in `README.md` sections 1–4 from the recordings: run results, the run 1 loop diagram, the system prompt/tools/injected context anatomy, and the numbers table with API-equivalent cost for runs 2–4 | Writing sections 5 and 6 (what surprised me, what I'll copy in M4) myself |
| 2026-11-22 | Claude Code | Wrote out "What surprised me" point 1 from my answers (the cost and caching sentences, at my request) | Chose the surprise (the whole conversation is resent every turn) and confirmed I expected the model to remember between turns |
| 2026-11-22 | Claude Code | Explained the memory index vs `CLAUDE.md` and wrote "What surprised me" point 2 (the memory line that changed what the agent edited), at my request | Chose the surprise and asked for the breakdown |
| 2026-11-22 | Claude Code | Wrote "What surprised me" point 3 (same prompt, different path), at my request; counted lines changed per diff | Chose the surprise |
| 2026-11-22 | Claude Code | Corrected the line counts in `tracing-claude-code.md` (runs 1–3 add 51–52 lines each; the old 98/70/72 included the first attempt) | Asked for the fix |
| 2026-11-22 | Claude Code | Removed a stray terminal prompt line from `tracing-claude-code.md` | Asked for it |
| 2026-11-22 | Claude Code | Explained why the same prompt gives different runs (sampling, snowballing tool results, inputs differing by 5 tokens) and added the 5-token evidence to point 3 | Asked why and chose to add it |
| 2026-11-22 | Claude Code | Explained that the prompt cache lives on Anthropic's servers and wrote section 6 point 1 (fixed, cacheable prompt prefix), at my request | Chose the point |
| 2026-11-22 | Claude Code | Wrote section 6 point 2 (rules in the prompt, notes loaded on demand), at my request | Chose the point |
| 2026-11-22 | Claude Code | Updated `NEXT_STEPS.md`: trace dissection marked done (section 7 left as TODO), `AGENTS.md` task made next | Asked for it |
