# Audit Methodology: How to Review an Agent Codebase

This is the step-by-step process for auditing an existing AI agent codebase — whether you're reviewing your own code or evaluating someone else's.

---

## Step 1: Find the Loop (5 minutes)

The agent loop is the heart of the system. Find it first.

**What to look for**:
- A `while` loop or recursive function that calls an LLM API
- The term "tool_call" or "function_call" near the LLM call
- A function named `run`, `execute`, `process`, `converse`, or `agent`

**Questions to answer**:
- Is it a flat loop, nested loop, or SDK-driven?
- Where is the iteration counter?
- Where is the retry logic?
- Where is the interrupt check?

**Red flags at this stage**:
- Can't find the loop (ad-hoc LLM calls scattered everywhere)
- No iteration limit
- No retry logic
- No interrupt mechanism

---

## Step 2: Trace a Tool Call End-to-End (10 minutes)

Pick one tool — preferably a simple one like `read_file` or `ls`. Trace its entire lifecycle:

1. **Where is the tool defined?** (schema, description, handler)
2. **How does it get registered?** (manual import list? self-registration? closure factory?)
3. **How does the LLM know about it?** (injected into system prompt? appended to messages?)
4. **How does the loop detect a tool call?** (parsing text? structured `tool_calls` field?)
5. **How are arguments validated?** (schema check? type coercion? repair?)
6. **How is the tool executed?** (direct call? thread pool? queue?)
7. **How is the result fed back?** (formatted as tool message? prepended to conversation?)

**Red flags**:
- No schema validation on arguments
- Tools can throw exceptions
- No result size capping
- Same-file mutations not serialized

---

## Step 3: Read the System Prompt Assembly (10 minutes)

Find the code that builds the system prompt and answer:

1. **Is it layered?** (identity → tools → behavior → context → knowledge) or monolithic?
2. **Is it frozen after first build?** (built once and cached) or rebuilt every call?
3. **Where does dynamic content go?** (system prompt or user messages?)
4. **What's the total size?** (under 5K tokens is good, 10K+ is concerning)

**Red flags**:
- System prompt mutated mid-session (cache killer)
- Dynamic content (memories, skills) injected into system prompt
- No platform-specific hints if multi-platform
- Tool descriptions are bare ("Reads a file")

---

## Step 4: Check Context Management (10 minutes)

1. **Is there compaction?** Search for "compact", "summarize", "truncate", "prune"
2. **What's the trigger threshold?** (40-60% of model limit is standard)
3. **Is the summary structure meaningful?** (resolved/pending/decisions) or just text compression?
4. **Is there a memory system?** (built-in, external plugins, session search?)
5. **How is memory injected?** (system prompt or user messages?)

**Red flags**:
- No compaction (fails on long conversations)
- Context window errors not handled
- No memory system (amnesiac agent)

---

## Step 5: Audit the Safety Layer (10 minutes)

1. **Is there prompt hardening?** Search for "trust", "untrusted", "evidence", "instruction"
2. **Are there approval gates?** (destructive operations require confirmation?)
3. **Are there pending actions?** (irreversible effects create drafts?)
4. **Is there rate limiting?** Per tool, per session, per minute?
5. **Is there budget tracking?** (token, cost, or iteration limits)

**Red flags**:
- Direct side effects (email, deploy, delete without confirmation)
- No rate limits
- No prompt hardening when processing external content
- No budget tracking

---

## Step 6: Review the Provider Layer (5 minutes)

1. **Is the provider abstracted?** (interface or adapter) or hardcoded strings?
2. **How many providers are supported?** (1 = risk, 2-3 = good, 4+ = resilient)
3. **Is there a fallback chain?** (try OpenAI, fall back to Anthropic, fall back to Google)
4. **How are errors classified?** (rate limit vs server error vs auth error)

**Red flags**:
- Hardcoded `openai.chat.completions.create(model="gpt-4o", ...)` everywhere
- No fallback model
- API errors crash the agent

---

## Step 7: Check Extensibility (5 minutes)

1. **Can new tools be added without modifying the core loop?**
2. **Can new providers be added without touching the agent loop?**
3. **Are there lifecycle hooks?** (pre/post LLM call, pre/post tool call)
4. **Is there a plugin system?** (only needed if third parties will extend the agent)

---

## Step 8: Score and Report

Use the 25-point checklist from SKILL.md Section 8. Score each item as pass (1), fail (0), or partial (0.5).

### Report Template

```markdown
# Agent Audit Report: [Codebase Name]

## Summary
- **Score**: 18/25 (72%)
- **Overall**: Solid foundation with critical gaps in safety and context management.
- **Priority fixes**: [Top 3 issues]

## Loop Audit (Score: X/5)
- [Item 1]: PASS/FAIL — [Brief explanation]
- ...

## Tool Audit (Score: X/6)
- ...

## Context Audit (Score: X/4)
- ...

## Prompt Audit (Score: X/4)
- ...

## Safety Audit (Score: X/4)
- ...

## Extensibility Audit (Score: X/2)
- ...

## Critical Issues (Severity: HIGH)
1. **No compaction** — Agent will fail on conversations longer than ~10 turns.
   Fix: Implement compaction at 40-60% model limit. See `references/context-management.md`.
2. **Direct side effects** — `send_email` tool sends immediately, no user confirmation.
   Fix: Implement pending action pattern. See `references/safety-architecture.md`.
3. ...

## Recommendations
1. [Incremental fixes, ordered by impact/effort ratio]
2. ...

## Architecture Diagram
[ASCII or brief description of the current architecture]
```

---

## Quick Audit (5-Minute Version)

For a rapid health check, answer just these:

1. **Is there a clear while-loop calling an LLM?** (Yes/No)
2. **Is there a max iteration limit?** (Yes/No — what value?)
3. **Does the system prompt change mid-session?** (Yes/No)
4. **Do tools crash or return errors?** (Crash/Return)
5. **Is there any form of compaction?** (Yes/No)
6. **Do destructive operations require user approval?** (Yes/No)
7. **Are there pending actions for irreversible effects?** (Yes/No)
8. **Is the provider abstracted?** (Yes/No — how many providers?)

If you answered "No" to 3+ of these, the agent has significant architectural issues.

---

## Automated Pre-Scan

Before manual audit, run the automated scanner:

```bash
python scripts/audit-scanner.py /path/to/agent/codebase
```

This flags mechanical red flags (file sizes, missing patterns, hardcoded strings) and produces a JSON report. Use this to focus your manual audit on the areas most likely to have issues.
