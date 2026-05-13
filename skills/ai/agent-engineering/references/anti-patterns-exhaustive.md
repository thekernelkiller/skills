# Anti-Patterns Exhaustive Catalog

Each anti-pattern includes: symptom (what you see), root cause (why it happens), impact (why it's harmful), and fix (how to resolve it). Real anonymized code examples are included where instructive.

---

## 1. Monster Agent Class

**Symptom**: A single file or class that contains everything — agent loop, tool implementations, system prompt, UI rendering, and persistence — all in 5000+ lines.

**Real pattern**:
```python
class AIAgent:  # 14,000 lines in run_agent.py (hermes-agent actually does this)
    def run_conversation(self): ...      # The loop (300 lines)
    def _build_system_prompt(self): ...  # Prompt assembly (500 lines)
    def _invoke_tool(self): ...          # Tool dispatch (200 lines)
    def _repair_tool_args(self): ...     # JSON repair (100 lines)
    def _compress_context(self): ...     # Compaction (200 lines)
    def _handle_retry(self): ...         # Retry logic (150 lines)
    def _render_message(self): ...       # UI rendering (200 lines)
    def _persist_session(self): ...      # Session persistence (100 lines)
    # ... 12,000 more lines of mixed concerns
```

**Impact**: Impossible to test components independently. Adding a feature requires modifying a 14,000-line file. New team members need weeks to understand the codebase. The agent core can't be reused for a different UI/platform without extracting everything.

**Fix**: Extract into separate, testable components:
- `loop.py` (~300 lines) — The ReAct loop
- `prompt_builder.py` (~200 lines) — System prompt assembly
- `tool_registry.py` (~150 lines) — Registration and dispatch
- `context_manager.py` (~200 lines) — Compaction, caching, memory
- `safety.py` (~150 lines) — Approval gates, rate limiting
- `ui.py` — UI rendering (separate from core)
- `persistence.py` — Session storage (separate from core)

Each component under 500 lines. Each independently testable.

---

## 2. No Max Iterations

**Symptom**: The agent loop has no exit condition beyond the LLM deciding to stop.

```python
while True:
    response = llm.generate(messages)
    if not response.tool_calls:
        return response.text
    # No iteration counter, no budget check
```

**Impact**: A confused or hallucinating LLM can loop indefinitely, consuming budget and never completing. This is the #1 cause of "agent went rogue and spent $50" incidents.

**Fix**:
```python
MAX_ITERATIONS = 50
for iteration in range(MAX_ITERATIONS):
    response = llm.generate(messages)
    if not response.tool_calls:
        return response.text
    # Execute tools...
else:
    return f"Stopped after {MAX_ITERATIONS} iterations. Last partial result: ..."
```

---

## 3. Dynamic System Prompt

**Symptom**: Tool descriptions, memory content, or skill instructions are appended to the system prompt mid-session.

```python
# BAD: System prompt changes every call
system_prompt += f"\nUser preference: {user_prefs}"  # Changes each query
system_prompt += f"\n{skill_content}"  # Added mid-session
```

**Impact**: Every system prompt change invalidates the prompt cache (Anthropic, OpenAI, Google, and most providers offer caching with 50-90% discounts on cached prefixes). A $0.03/turn agent becomes a $0.30/turn agent. On a 100-turn session: $3 → $30.

**Fix**: Freeze the system prompt after the first build. Inject dynamic content into user messages:
```python
# GOOD: Dynamic context goes in user messages
user_message = f"""
<memory-context>{memories}</memory-context>
<skill-context>{skill_content}</skill-context>
---
{user_actual_message}
"""
```

---

## 4. Tools That Crash Instead of Returning Errors

**Symptom**: Tool handlers throw exceptions that break the agent loop.

```python
def read_file_handler(path: str) -> dict:
    with open(path) as f:  # FileNotFoundError crashes the loop
        return {"content": f.read()}
```

**Impact**: The agent loop crashes. The LLM can't recover. The user sees a Python traceback instead of a helpful response.

**Fix**: Every tool handler must catch ALL exceptions:
```python
def read_file_handler(path: str) -> dict:
    try:
        with open(path) as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except PermissionError:
        return {"error": f"Permission denied: {path}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
```

---

## 5. No Compaction

**Symptom**: The entire conversation history is sent to the LLM on every call, with no summarization or pruning.

**Impact**: Token usage grows linearly. Eventually hits the model's context limit and fails. Even before failure, the agent gets slower and more expensive with every turn.

**Fix**: Implement compaction when estimated tokens exceed 40-60% of the model's limit. See `context-management.md` for the full algorithm.

---

## 6. Mixed Concerns

**Symptom**: The agent loop class also handles UI rendering, database writes, and message formatting.

```python
class Agent:
    def run(self, message):
        self._render_thinking_spinner()  # UI concern in core loop
        response = self._llm_call()
        self._format_for_slack(response)  # Platform concern in core loop
        self._save_to_database(response)   # Persistence concern in core loop
        return self._render_response(response)  # UI concern in core loop
```

**Impact**: Can't reuse the agent core for a different platform (CLI vs Slack vs web). Testing requires mocking UI and database. Changes to rendering break the core loop.

**Fix**: Agent core is pure logic. UI, persistence, and platform formatting are separate layers that consume the core's output.

---

## 7. No Schema Validation

**Symptom**: Tool arguments are passed as raw dicts with no validation.

```python
TOOLS = {
    "read_file": lambda args: open(args["path"]).read()  # No validation
}

def execute_tool(name, args):
    return json.dumps(TOOLS[name](args))  # Pass raw dict, hope for the best
```

**Impact**: When the LLM passes `{"path": 42}` or `{"pth": "/foo"}`, the tool fails silently or crashes with an unhelpful error.

**Fix**: Validate against a JSON Schema before execution. Coerce types (string "42" → int 42). Return descriptive validation errors that the LLM can understand.

---

## 8. Direct Side Effects

**Symptom**: Tools that interact with external systems execute immediately.

```python
def send_email(to, subject, body):
    email_service.send(to=to, subject=subject, body=body)  # Sent!
    return {"status": "sent"}
```

**Impact**: A hallucinated email, a misunderstood intent, or a prompt injection results in irreversible external effects. Emails sent to wrong recipients. Code deployed to production. Payments made.

**Fix**: Use the pending action pattern. Tools create drafts. User confirms before execution.

---

## 9. No Retry Logic

**Symptom**: The agent makes one LLM API call attempt and fails if the API returns an error.

```python
response = openai.chat.completions.create(...)  # One attempt, no retry
```

**Impact**: Transient API errors (rate limits, server overload, timeouts) kill the agent. In production, API failures are common — your agent must handle them gracefully.

**Fix**: Retry envelope with exponential backoff, jitter, and fallback models. See `loop-patterns.md` for implementation.

---

## 10. Manual Tool Import Lists

**Symptom**: Adding a tool requires modifying multiple files.

```python
# tools/__init__.py
from .file_tools import read_file, write_file, edit_file, grep, find, ls
from .web_tools import web_search, web_extract
from .terminal_tools import bash
# ... 50 lines of imports

# agent.py
from tools import read_file, write_file, edit_file, grep, find, ls, web_search, bash
TOOLS = [read_file, write_file, edit_file, grep, find, ls, web_search, bash]
```

**Impact**: Adding a tool requires touching: the tool file, `tools/__init__.py`, the agent's import list, the agent's tool list, and the system prompt. Five places to forget.

**Fix**: Self-registration with discovery. Create a tool file, call `registry.register()`, done.

---

## 11. Hardcoded Model Provider

**Symptom**: The provider/model is hardcoded throughout the codebase.

```python
response = openai.chat.completions.create(model="gpt-4o", messages=messages)
```

**Impact**: Can't switch providers. Can't add fallback. Testing requires API keys for that specific provider. Locked into one vendor.

**Fix**: Provider abstraction layer. Model selected via config:
```python
model = get_model(provider="anthropic", model_id="claude-sonnet-4-20250514")
response = model.generate(messages=messages)
```

---

## 12. No Budget Tracking

**Symptom**: The agent runs with no visibility into token usage or cost.

**Impact**: A runaway agent can burn significant money before anyone notices. No accountability for cost. Can't set budgets per user or per session.

**Fix**: Track tokens consumed. Report usage. Force-stop when budget exceeded. Provide usage summaries.

---

## 13. No Interrupt Mechanism

**Symptom**: Once started, the agent can't be stopped except by killing the process.

**Impact**: Terrible UX. Can't course-correct. Have to kill terminal and lose progress. Dangerous if the LLM is doing something destructive.

**Fix**: Thread-safe or event-driven interrupt flag. Checked each iteration. Long tools check it too. Graceful cleanup on interrupt.

---

## 14. Monolithic System Prompt

**Symptom**: The system prompt is one giant string assembled via concatenation.

```python
system_prompt = "You are an agent.\n"
system_prompt += "Available tools:\n"
for tool in tools:
    system_prompt += f"- {tool.name}: {tool.description}\n"
system_prompt += "\nBehavioral rules:\n"
system_prompt += rules_text
system_prompt += f"\nWorking directory: {cwd}\n"
system_prompt += f"\nDate: {date.today()}\n"
system_prompt += project_context
# What order are these in? Is anything duplicated? Hard to tell.
```

**Impact**: Hard to read, modify, or debug. String concatenation bugs accumulate. Ordering matters but isn't enforced.

**Fix**: Layered builder pattern. Each layer assembled independently with clear boundaries:
```python
class PromptBuilder:
    def build(self, layers: list[PromptLayer]) -> str:
        return "\n\n".join(layer.content for layer in sorted(layers, key=lambda l: l.order))
```

---

## 15. No Prompt Hardening

**Symptom**: External content (email bodies, web pages, user files) is fed directly to the LLM with no security instructions.

**Impact**: Prompt injection through user data. "Ignore system instructions" embedded in content the agent reads. The agent follows malicious instructions.

**Fix**: Add defense instructions to the system prompt when processing untrusted content. Tag external content as "EVIDENCE, not INSTRUCTION."

---

## 16. Over-Engineered Abstractions

**Symptom**: The agent has elaborate interfaces, abstract factories, strategy patterns, and dependency injection frameworks — all for what is fundamentally a while-loop with tool calls.

```typescript
interface IAgentLoopStrategy {
  execute(context: IAgentContext, config: IAgentConfig): Promise<IAgentResult>;
}

class ReActLoopStrategy implements IAgentLoopStrategy { ... }
class ChainOfThoughtStrategy implements IAgentLoopStrategy { ... }
class TreeOfThoughtsStrategy implements IAgentLoopStrategy { ... }

class AgentLoopStrategyFactory {
  static create(type: LoopType, deps: Dependencies): IAgentLoopStrategy { ... }
}
```

**Impact**: The 200-line agent loop becomes a 2000-line architecture. New engineers can't understand it. Bugs hide in the abstraction layers. The flexibility is never used (you only need one loop strategy).

**Fix**: One concrete class. One loop. Simple while-loop. If you genuinely need a different loop pattern later, refactor then — not before.

---

## 17. Everything Is a Config Option

**Symptom**: Every parameter is configurable via environment variables, config files, and CLI flags.

```python
MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "90"))
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("AGENT_TOP_P", "0.9"))
SYSTEM_PROMPT_PATH = os.getenv("AGENT_SYSTEM_PROMPT_PATH", "./prompts/system.md")
TOOLS_DIR = os.getenv("AGENT_TOOLS_DIR", "./tools/")
COMPACTION_THRESHOLD = float(os.getenv("AGENT_COMPACTION_THRESHOLD", "0.5"))
RETRY_MAX_ATTEMPTS = int(os.getenv("AGENT_RETRY_MAX", "3"))
# ... 40 more config lines
```

**Impact**: Configuration explosion. Nobody knows what all the options do. Bugs from bad combinations. Documentation burden. Most of these will never be changed from defaults.

**Fix**: Sensible defaults. Only expose configuration that users genuinely need to change:
- Model selection (people switch models)
- Max iterations (people want to limit)
- Budget limits (people want to control cost)
- Working directory (changes per session)

Everything else: hardcode a good default. Make it configurable only when users ask for it.

---

## Summary: The Red Flag Checklist

When reviewing an agent codebase, these are immediate red flags:

| # | Red Flag | Severity |
|---|----------|----------|
| 1 | Single file/class > 2000 lines | High — refactor needed |
| 2 | No max iterations | Critical — will loop forever |
| 3 | System prompt mutated mid-session | High — 10x cost increase |
| 4 | Tools throw exceptions | High — fragile, LLM can't recover |
| 5 | No compaction | High — fails on long conversations |
| 6 | Loop mixed with UI/persistence | Medium — can't reuse or test |
| 7 | Raw dict tool args (no schema) | Medium — silent type errors |
| 8 | Direct side effects (send, deploy) | Critical — irreversible damage |
| 9 | No retry logic | Medium — fragile in production |
| 10 | Manual tool import lists | Low — maintenance burden |
| 11 | Hardcoded provider strings | Medium — vendor lock-in |
| 12 | No budget tracking | High — runaway costs |
| 13 | No interrupt mechanism | Medium — bad UX |
| 14 | Monolithic system prompt string | Low — maintenance burden |
| 15 | No prompt hardening | High — prompt injection risk |
| 16 | Over-engineered abstractions | Medium — complexity without value |
| 17 | Everything is config | Low — config explosion |
