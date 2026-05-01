# Context Management: Compaction, Caching, and Memory

## The Four Context Tiers

Every agent should organize context into four tiers based on how often they change:

### Tier 1: Frozen Prefix (system prompt)

**What**: Agent identity, tool catalog, behavioral rules, operational facts.
**Lifetime**: Built once at session start. Never modified.
**Size**: Typically 2-5K tokens.
**Caching**: Full prompt cache prefix (via provider-specific cache markers like Anthropic's `cache_control` or OpenAI's `cached`). 50-90% discount after first call.

```python
class SystemPrompt:
    """Frozen after first build. Never mutated mid-session."""
    
    def __init__(self):
        self._built = False
        self._content = ""
    
    def build(self, identity: str, tools: list, rules: str, context: str) -> str:
        if self._built:
            return self._content  # Return cached, do NOT rebuild
        
        layers = [
            identity,
            self._format_tools(tools),
            rules,
            context,
        ]
        self._content = "\n\n".join(layers)
        self._built = True
        return self._content
    
    def get(self) -> str:
        """Always returns the same content. Immutable after build()."""
        return self._content
```

### Tier 2: Persistent Memory (rarely changes)

**What**: User preferences, learned facts, environment details.
**Lifetime**: Persists across sessions. Changes only when explicitly updated.
**Size**: Variable, typically 200-1000 tokens.
**Placement**: Can go in system prompt (may invalidate cache on update) or in user messages.

### Tier 3: Session Context (changes per turn)

**What**: Memory prefetch results, rule state changes, compaction summaries.
**Lifetime**: Injected before each user message. Session-scoped.
**Size**: Variable, typically 50-500 tokens.
**Placement**: ALWAYS in user messages. Never in system prompt.

### Tier 4: Ephemeral Context (API-call time only)

**What**: Temporary overrides, per-call guidance, steering messages.
**Lifetime**: One API call. Never persisted.
**Size**: Typically <200 tokens.
**Placement**: Prepended to the message list for one call. Not stored in conversation.

---

## Compaction: The Full Algorithm

Compaction is the process of summarizing old conversation turns to stay within context limits.

### When to Compact

```python
def should_compact(conversation: list, model_limit: int, threshold: float = 0.5) -> bool:
    """Compact when estimated tokens exceed threshold of model limit."""
    estimated = estimate_tokens(conversation)
    return estimated > model_limit * threshold
```

Trigger at 40-60% of the model's context limit. Don't wait until overflow — that's too late.

### The Compaction Algorithm

```python
def compact(conversation: list, model_limit: int, compact_llm) -> list:
    """
    Compact conversation history.
    Returns new conversation with prefix messages replaced by summary.
    """
    # Step 1: Find cut point — keep last N messages, summarize the rest
    recent_budget = int(model_limit * 0.4)  # Keep 40% for recent context
    prefix_messages, kept_messages = find_cut_point(conversation, recent_budget)
    
    if not prefix_messages:
        return conversation  # Nothing to compact
    
    # Step 2: Generate summary
    summary = generate_summary(prefix_messages, compact_llm)
    
    # Step 3: Replace prefix with summary as a user message
    compacted = [
        conversation[0],  # System prompt always stays
        {
            "role": "user",
            "content": f"<compaction-summary>\n{summary}\n</compaction-summary>"
        },
        *kept_messages,
    ]
    
    return compacted


def find_cut_point(messages: list, recent_token_budget: int) -> tuple:
    """Split messages into prefix (to summarize) and kept (recent)."""
    # Always keep system prompt
    system = messages[0]
    rest = messages[1:]
    
    # Count tokens backward from the end until we hit budget
    kept = []
    tokens = 0
    for msg in reversed(rest):
        msg_tokens = estimate_message_tokens(msg)
        if tokens + msg_tokens <= recent_token_budget:
            kept.insert(0, msg)
            tokens += msg_tokens
    
    prefix = [system] + rest[:len(rest) - len(kept)]
    return prefix, kept


def generate_summary(prefix_messages: list, compact_llm) -> str:
    """Use a cheap LLM to summarize the prefix."""
    summary_prompt = f"""
    Summarize the following conversation between an AI agent and a user. 
    Focus on capturing:
    - RESOLVED: What was successfully completed or answered
    - PENDING: What questions or tasks remain unresolved
    - DECISIONS: What choices were made (technologies, approaches, etc.)
    - STATE: Any relevant state that was established (file paths, variable values, etc.)
    
    Be concise. This summary will be injected back into the conversation
    to provide context for the remaining turns.
    
    CONVERSATION:
    {format_messages_for_summary(prefix_messages)}
    """
    
    response = compact_llm.generate(summary_prompt)
    return response.text
```

### Summary Structure

The summary should follow this template:

```
RESOLVED QUESTIONS:
- The user confirmed using PostgreSQL for the database
- Authentication was implemented using JWT tokens
- The login endpoint was tested and works correctly

PENDING QUESTIONS:
- Whether to use Redis or Memcached for caching (user will decide later)
- Database migration strategy for production

REMAINING WORK:
- Implement the user profile endpoint
- Add rate limiting to the login endpoint
- Write integration tests for the auth flow

DECISIONS MADE:
- Database: PostgreSQL 16
- Auth: JWT with 1-hour expiry
- API framework: FastAPI
- Testing: Pytest with httpx

CONVERSATION SUMMARY:
The user asked the agent to implement authentication for their FastAPI application.
After discussing options, they chose JWT-based auth with PostgreSQL for user storage.
The agent created auth.py with login/register endpoints, added password hashing with
bcrypt, and wrote unit tests. The user then asked about caching — the agent recommended
Redis but the user wanted to evaluate Memcached first. The conversation ended with
the agent implementing the auth middleware.
```

Don't just compress text — preserve **meaning**. "We decided on PostgreSQL" is more important than the exact words used in the discussion.

---

## Prompt Caching Implementation

### Prompt Caching (Provider-Agnostic)

```python
import anthropic

class CachedAgent:
    def __init__(self, client, model, system_prompt):
        self.client = client
        self.model = model
        self._frozen_system = self._build_cached_system(system_prompt)
    
    def _build_cached_system(self, system_prompt: str) -> list:
        """Build system prompt with cache_control markers."""
        return [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # Cache this entire block
            }
        ]
    
    def call(self, messages: list) -> anthropic.types.Message:
        """Every call uses the SAME cached system prompt."""
        return self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self._frozen_system,  # Always identical → cache hits
            messages=messages,
        )
```

The key: `self._frozen_system` must be IDENTICAL across calls. Any change invalidates the cache.

### Cache Discipline Checklist

1. System prompt built ONCE at session start
2. Dynamic content (memories, skill content, rule state) → user messages
3. Tool definitions frozen for the session (new tools wait until next session)
4. User/system prompt overrides → ephemeral messages (not persisted)
5. Verify cache hits by checking response headers: `anthropic-...: cache-hit`

### Cache Economics

| Change to system prompt | Cache behavior |
|-------------------------|---------------|
| No changes (frozen) | Full cache hit on every call after the first |
| Add one character | Full cache MISS. Entire prefix re-uploaded. |
| Change tool description wording | Full cache MISS. |
| Reorder layers | Full cache MISS. |
| Add a new tool mid-session | Full cache MISS. |

One-line change = full cache invalidation. This is why the system prompt must be immutable.

---

## Memory Patterns

### Built-in Memory (hermes-agent style)

Simple key-value persistent store:

```python
class MemoryStore:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def save(self, key: str, value: str):
        self.db.execute("""
            INSERT INTO memories (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
        """, (key, value, value))
    
    def get_all(self) -> list[tuple[str, str]]:
        return self.db.execute("SELECT key, value FROM memories ORDER BY updated_at DESC LIMIT 50").fetchall()
    
    def format_for_prompt(self) -> str:
        memories = self.get_all()
        if not memories:
            return ""
        lines = ["## User Preferences and Memories", ""]
        for key, value in memories:
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
```

The formatted output goes into the system prompt (rarely changes) or a user message (injected before each turn). The agent calls a `save_memory` tool to persist facts.

### External Memory Providers

For more sophisticated use cases, plug in external providers:

```python
class MemoryManager:
    def __init__(self, builtin: MemoryStore, external_providers=None):
        self.builtin = builtin
        self.external = external_providers or []
    
    def prefetch(self, query: str) -> str:
        """Fetch relevant memories for the current query. Injected into user message."""
        contexts = []
        
        for provider in self.external:
            try:
                result = provider.prefetch(query)
                contexts.append(f"<memory-context source='{provider.name}'>\n{result}\n</memory-context>")
            except Exception:
                pass  # External provider failures shouldn't break the agent
        
        return "\n".join(contexts)
```

The `<memory-context>` fencing tags serve two purposes:
1. The LLM can identify what's externally retrieved vs part of the user's actual message
2. The agent can scrub memory context for privacy when exporting conversations

### Session Search (hermes-agent's FTS5 approach)

```python
class SessionSearch:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                session_id, role, content, timestamp
            )
        """)
    
    def index_message(self, session_id: str, role: str, content: str):
        self.db.execute(
            "INSERT INTO sessions_fts VALUES (?, ?, ?, datetime('now'))",
            (session_id, role, content)
        )
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        results = self.db.execute(
            "SELECT session_id, role, content, rank FROM sessions_fts WHERE sessions_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit)
        ).fetchall()
        return [{"session_id": r[0], "role": r[1], "content": r[2][:500]} for r in results]
```

The agent has a `session_search` tool. When it needs to recall past conversations, it searches FTS5, finds relevant chunks, then summarizes them with an LLM before presenting results. This creates genuine long-term memory without needing a vector database.

### Memory Nudge Pattern

After each agent turn, the agent prompts itself:

```
Based on the conversation so far, is there any information worth remembering
for future interactions? Consider:
- User preferences expressed
- Technical decisions made
- Environment details discovered
- Errors encountered and their resolutions

If yes, call save_memory. If no, continue.
```

This closes the learning loop. The agent improves from experience without fine-tuning.

---

## Token Estimation

Fast, approximate token counting (don't need the exact tokenizer — just close enough for budget decisions):

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 characters per token for English text."""
    return len(text) // 4

def estimate_message_tokens(msg: dict) -> int:
    """Estimate tokens for a conversation message."""
    content = msg.get("content", "")
    if isinstance(content, list):
        # Multi-part content (text + images)
        total = 0
        for part in content:
            if part.get("type") == "text":
                total += estimate_tokens(part["text"])
            elif part.get("type") == "image_url":
                total += 300  # Rough estimate for image tokenization
        return total
    return estimate_tokens(str(content))

def estimate_conversation_tokens(conversation: list) -> int:
    """Estimate total tokens for the full conversation."""
    return sum(estimate_message_tokens(msg) for msg in conversation)
```

For precise counting, use the provider's tokenizer (e.g., `tiktoken` for OpenAI). But for budget decisions, the 4-char-per-token heuristic is fast and close enough.

---

## Context Injection Pattern

When injecting dynamic context, place it BEFORE the current user message, not in the system prompt:

```python
def build_messages(conversation, memories, rule_state, inbox_stats):
    messages = []
    
    # System prompt (frozen, cached) goes first
    # ... (handled separately via provider-specific system param)
    
    # Previous conversation turns
    for msg in conversation[:-1]:  # All except the last user message
        messages.append(msg)
    
    # Injected context (EPHEMERAL — goes before current user message)
    injected = []
    
    if inbox_stats and is_first_message(conversation):
        injected.append(f"Current inbox: {inbox_stats}")
    
    if memories:
        injected.append(f"<memory-context>\n{memories}\n</memory-context>")
    
    if rule_state and rules_have_changed(rule_state):
        injected.append(f"<rule-context>\n{rule_state}\n</rule-context>")
    
    if injected:
        messages.append({
            "role": "user",
            "content": "\n\n".join(injected)
        })
    
    # The actual user message
    messages.append(conversation[-1])  # The current user message
    
    return messages
```

This:
1. Preserves the frozen system prompt (cache)
2. Gives the LLM the dynamic context it needs
3. Keeps the user message as the last thing the LLM sees
4. Doesn't break the user/assistant role alternation requirement that many LLM APIs enforce
