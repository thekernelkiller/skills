# Quick Reference: Agent Engineering Cheat Sheet

## The 10 Things Every Agent MUST Have

1. **A ReAct loop** — While-loop: call LLM → if tool calls, execute → feed back → repeat. Max 200 lines.
2. **Max iteration limit** — Hard cap (25-90). Prevents infinite loops and runaway costs.
3. **Retry with exponential backoff** — LLM APIs fail. Retry rate limits, server errors, timeouts. Don't retry auth errors.
4. **Error-as-result pattern** — Tools NEVER crash. Return `{"error": "..."}` as result text. The LLM recovers.
5. **Compaction** — Summarize old turns when approaching context limits. Don't let the agent hit the wall.
6. **Frozen system prompt** — Built once at session start. Never modified. Preserves prompt cache (50-90% discount).
7. **Tool schema validation** — Validate + coerce args before execution. String "42" → int 42.
8. **Approval gates** — Destructive operations require user confirmation. At minimum, ask the first time.
9. **Pending actions** — Irreversible external effects (email, deploy, payment) create drafts, not direct execution.
10. **Budget tracking** — Track tokens and cost. Force-stop when budget exceeded.

## The 5 Things Every Agent Should AVOID

1. **Monster class** — Single file >2,000 lines. Refactor into components (loop, tools, prompts, safety, context).
2. **Dynamic system prompt** — Mutating mid-session destroys cache. 10x cost increase for no benefit.
3. **Direct side effects** — Sending email, deploying code, charging payments immediately. Use pending actions instead.
4. **No schema validation** — Raw dict tool args. The LLM will produce wrong types. Validate and coerce.
5. **Over-engineering** — Abstract factories, strategy patterns, plugin architectures before you need them. Start simple.

## Component Sizing Guide

| Component | Target lines | Max lines |
|-----------|-------------|-----------|
| Agent loop | 200-300 | 500 |
| Tool registry | 100-200 | 300 |
| System prompt builder | 100-200 | 300 |
| Context manager (compaction) | 200-300 | 500 |
| Safety layer | 100-200 | 300 |
| Provider adapter (per provider) | 100-200 | 300 |
| Single tool implementation | 50-200 | 500 |

## When to Add Complexity

The order of evolution for a new agent:

```
Phase 1: Core loop (200 lines)
  └── Simple while-loop, 3 tools, explicit registry, basic system prompt

Phase 2: Safety (add ~200 lines)
  └── Approval gates, prompt hardening, budget tracking

Phase 3: Context management (add ~300 lines)
  └── Compaction, memory, prompt caching awareness

Phase 4: Provider flexibility (add ~200 lines)
  └── Abstraction layer, fallback chains, error classification

Phase 5: UX/Platform (lines depend on platforms)
  └── TUI, web UI, messaging bots — all share the same agent core

Phase 6: Extensibility (add ~500 lines)
  └── Lifecycle hooks, extension API, tool registration API
  └── ONLY if third parties will build on your agent
```

Never jump to Phase 6 before Phase 1. Never add extensibility before you need it.

## Context Injection Rules

| Where content changes | Where to put it |
|----------------------|-----------------|
| Never changes | System prompt (cached) |
| Changes rarely (preferences) | System prompt or user message |
| Changes per query (memories) | User message (before current message) |
| Changes per session (compaction) | User message |
| Changes per call (overrides) | Ephemeral (never persisted) |

## Safety Priority Order

When adding safety to an existing agent:

1. **Pending actions** (if irreversible side effects exist) — CRITICAL
2. **Approval gates** (if destructive tools exist) — HIGH
3. **Prompt hardening** (if processing external content) — HIGH
4. **Budget tracking** (if users can spend money) — HIGH
5. **Tool guardrails** (before production deployment) — MEDIUM

## Red Flag Scanner

Run `scripts/audit-scanner.py` on any codebase. It flags:
- Files over 2000 lines
- Missing max_iterations
- Dynamic system prompt modification
- Tools with no schema validation
- No compaction logic
- Direct external side effects
- Hardcoded provider/model strings

## Key Numbers

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Core file size | <500 lines | 500-2000 lines | >2000 lines |
| System prompt size | <3K tokens | 3-10K tokens | >10K tokens |
| Tool count | 3-20 | 20-50 | 50+ (needs toolset system) |
| Max iterations | 25-90 | 90-200 | >200 or unlimited |
| Compaction threshold | 40-60% of limit | 60-80% | >80% or none |
| Cache hit rate (if applicable) | >80% | 50-80% | <50% |
| Provider count | 2-3 | 1 | 0 (hardcoded) |
