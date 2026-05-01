# System Prompt Engineering: The Layered Approach

## Why Layers Matter

A well-structured system prompt is like well-structured code: each layer serves a specific purpose, has clear boundaries, and can be modified independently. A monolithic 2000-line blob is hard to understand, debug, and evolve.

---

## The Five-Layer Template

```
──────────────────────────────────────
LAYER 1: IDENTITY
──────────────────────────────────────
You are an expert coding assistant. Your goal is to help users write,
understand, debug, and refactor code. You work inside pi, a coding agent
harness that provides you with tools for reading files, executing
commands, and editing code.

Be concise. Show file paths when working with files. Explain your
reasoning only when the user asks for it.
──────────────────────────────────────
LAYER 2: TOOL CATALOG
──────────────────────────────────────
Available tools:
- read: Read file contents at a path. Use offset/limit for large files.
- write: Create or overwrite a file. Auto-creates parent directories.
- edit: Replace exact text in a file. old_str must match exactly once.
- bash: Execute a shell command. Prefer specialized tools when available.
- grep: Search file contents with regex patterns.
- find: Find files by name pattern.
- ls: List directory contents.
──────────────────────────────────────
LAYER 3: BEHAVIORAL RULES
──────────────────────────────────────
When working with code:
- Read files before editing them to understand current content
- Use the most specific tool available (grep > bash rg, find > bash find, ls > bash ls)
- When editing, prefer minimal changes — edit the specific lines that need changing
- Make related changes together in one edit call (use multiple edits in one call)
- When running commands, briefly explain what the command does
- When you encounter errors, read the error message carefully and try to fix the root cause

Safety rules:
- Never make destructive changes without explaining what you're doing
- If a user asks to delete files or run dangerous commands, ask for confirmation
- Do not execute commands that modify system configuration without explicit permission
──────────────────────────────────────
LAYER 4: OPERATIONAL CONTEXT
──────────────────────────────────────
Current date: 2026-05-01
Current working directory: /Users/alice/projects/myapp
Platform: macOS (darwin)
Shell: zsh
──────────────────────────────────────
LAYER 5: PROJECT KNOWLEDGE
──────────────────────────────────────
Project context from AGENTS.md:
- This is a Next.js 15 application with Tailwind CSS
- Database: PostgreSQL accessed via Prisma ORM
- Tests: Vitest + React Testing Library
- Use pnpm, not npm
- Components use shadcn/ui patterns
──────────────────────────────────────
```

---

## Layer 1: Identity — Detailed Design

The identity layer answers: "Who am I? What is my purpose? How should I communicate?"

A good identity statement:
- Names the agent and its context ("coding assistant inside pi")
- States the goal (what "good" looks like)
- Sets the communication tone (concise, file paths, no unnecessary explanation)
- Is 3-5 lines max

The identity should be specific enough to guide behavior but general enough to handle diverse requests. "You are an expert coding assistant" is better than "You are a Python Django expert" because it doesn't constrain the tools the agent will use.

---

## Layer 2: Tool Catalog — Detailed Design

The tool catalog is a one-line summary per tool. The model scans this to know what's available.

Each tool entry should contain:
- **Name**: Exact tool name as registered
- **What**: One-line description of what it does
- **When**: Hint about when to use it (especially vs similar tools)
- **Gotcha**: Critical edge case the model should know

```
- read: Read file contents at a path. Use offset/limit for large files.
  Images are returned with dimension metadata but not pixel data.

- edit: Replace exact text in a file. old_str must match EXACTLY once.
  For creating new files, use the write tool instead.

- bash: Execute a shell command with configurable timeout.
  Prefer grep, find, and ls when those tools are available.
```

The difference between good and bad tool entries:

BAD: `"read: Reads a file."` — The model knows it can read, but not how to handle large files, images, or truncation.

GOOD: `"read: Read file contents at a path. Use offset/limit when files exceed 500 lines — output is capped at 100K chars and truncated results include a hint to continue with offset=N. Images are returned as metadata (dimensions, format) not pixel data."` — The model now knows the tool's limits and how to work within them.

---

## Layer 3: Behavioral Rules — Detailed Design

Behavioral rules are the "how to work" instructions. They should be specific, actionable, and explainable.

### Write rules that explain WHY

Instead of: `"ALWAYS read files before editing them"`, write: `"Read files before editing them to understand current content and avoid making incorrect changes."`

The "why" helps the model apply the rule correctly when the situation is ambiguous. "ALWAYS" without explanation leads to either rigid over-application or the model ignoring it as boilerplate.

### Conditional rules

```
When bash is available but grep/find/ls are not: "Use bash for file operations like rg, find, and ls since specialized tools are not available."

When all tools are available: "Prefer grep over bash rg, find over bash find, and ls over bash ls. These tools are faster and produce more structured output."
```

### Safety rules that are hard boundaries

Safety rules should be unconditional:
```
"Never execute commands that modify system configuration (brew install, apt-get, pip install --global) without explicit user permission."
"Never delete files without confirming with the user first."
```

vs softer guidance:
```
"Be concise in your responses. Show file paths clearly when working with files."
```

---

## Layer 4: Operational Context — Detailed Design

This layer is pure facts: date, time, OS, shell, working directory, available tools. Things the model cannot know and would guess wrong.

**Always include**:
- Current date (YYYY-MM-DD format) — LLMs default to their training cutoff
- Working directory (absolute path) — The model needs to know where files are
- Platform/OS (macOS/Linux/Windows) — Affects command syntax and file paths
- Shell (bash/zsh/fish) — Affects command syntax

**Optionally include**:
- Git branch — Gives the model context about what's being worked on
- Environment variables — If the model needs them
- Active virtual environment — Python version, Node version

---

## Layer 5: Project Knowledge — Detailed Design

This layer contains domain knowledge that the agent should always know: project conventions, technology stack, architectural decisions, coding standards.

**Sources**:
- `.cursorrules`, `.github/copilot-instructions.md` — IDE-provided instructions
- `AGENTS.md`, `CLAUDE.md` — Project-specific agent instructions
- `README.md` — Project overview
- `package.json`, `pyproject.toml` — Technology stack
- Skills loaded at session start

**What to include**:
- Technology stack (framework, language, database, tools)
- Coding conventions (tabs vs spaces, naming patterns, file organization)
- Architectural decisions (why we chose X over Y)
- Testing requirements (framework, coverage expectations)

**What NOT to include**:
- The entire README
- Package.json contents (extract only what matters)
- Git log
- File listings (the model can use tools for this)

---

## Frozen Prefix Discipline

The single most important economic decision in agent design: **the system prompt must be immutable after the first build**.

### Why

Prompt caching (available from Anthropic, OpenAI, Google, and many providers) gives a 50-90% discount on cached input tokens. The entire system prompt can be cached — but only if it's identical between calls. One character change = full cache miss = up to 10x cost increase.

### Implementation

```python
class SystemPromptBuilder:
    def __init__(self):
        self._built = False
        self._content = ""
    
    def build(self, identity, tools, rules, context, knowledge) -> str:
        if self._built:
            return self._content  # NEVER rebuild
        
        self._content = "\n\n".join([identity, tools, rules, context, knowledge])
        self._built = True
        return self._content
    
    def get_cached_content(self) -> str:
        return self._content
```

### What goes where

| Content type | System prompt (cached) | User message (dynamic) | Why |
|---|---|---|---|
| Agent identity | YES | NO | Never changes |
| Tool catalog (names + snippets) | YES | NO | Doesn't change mid-session |
| Behavioral rules | YES | NO | Boundaries never change |
| Operational context (date, cwd) | YES | NO | Built once at start |
| Project knowledge (AGENTS.md) | YES | NO | Read once at start |
| Memory prefetch results | NO | YES | Changes per query |
| Skill content loaded mid-session | NO | YES | Dynamic, per-request |
| Rule/system state changes | NO | YES | Only injected when changed |
| Compaction summaries | NO | YES | Generated mid-session |
| Inbox/domain stats | NO | YES | Changes per message |
| Temporary overrides | NO (ephemeral) | NO (ephemeral) | Per-call, never stored |

---

## Platform-Specific Hints

If your agent runs on multiple platforms (CLI, Slack, Telegram, web), add a small platform hint:

```
[When in Slack]: Format responses using Slack mrkdwn. Use numbered lists 
and bullet points. Keep responses under 3000 characters — Slack has message 
length limits. For code, use ``` blocks. For emails, use a numbered list format 
rather than HTML widgets.

[When in Telegram]: Format using Telegram's MarkdownV2. Keep messages concise. 
Split long responses across multiple messages rather than truncating mid-thought.

[When in CLI]: Use terminal formatting (colors via ANSI codes). Show file paths 
as relative paths. Support markdown rendering.
```

The hint changes per platform, but it's small (probably 10-20 lines per platform). This small investment dramatically improves output quality per platform.

---

## Skills and Knowledge Injection

When the user loads a skill or knowledge file mid-session, inject it as a user message, NOT as part of the system prompt:

```python
def load_skill(skill_name: str, skill_content: str, conversation: list):
    # WRONG: Modifying system prompt invalidates cache
    # system_prompt += f"\n\nSkill: {skill_name}\n{skill_content}"
    
    # RIGHT: Inject as user message — preserves cache
    conversation.append({
        "role": "user",
        "content": f"<skill name='{skill_name}'>\n{skill_content}\n</skill>\n\nFollow the instructions in this skill."
    })
```

Or as pi-mono does it, expand to an XML block in the user message:

```xml
<skill name="react-testing">
  <description>Patterns for testing React components with React Testing Library</description>
  <location>/Users/alice/.pi/skills/react-testing.md</location>
  <content>
    # React Testing Patterns
    ...
  </content>
</skill>
```

---

## System Prompt Checklist

Before finalizing a system prompt, verify:

- [ ] Identity is clear and specific (3-5 lines)
- [ ] Each tool has a one-line description with usage hint
- [ ] Behavioral rules explain WHY, not just WHAT
- [ ] Safety rules are unconditional hard boundaries
- [ ] Operational context includes date, cwd, platform, shell
- [ ] Project knowledge is extracted (not the whole README)
- [ ] Prompt is frozen after first build (immutable)
- [ ] Dynamic content injection path is clear (user messages)
- [ ] Platform-specific hints are included if multi-platform
- [ ] Total prompt size is under 5K tokens (leaving room for conversation)

---

## Real Example: pi-mono's System Prompt

Here's a real (abbreviated) system prompt from pi-mono to see the layers in practice:

```
You are an expert coding assistant operating inside pi, a coding agent harness.

Available tools:
- read: Read file contents. Use offset/limit for large files with truncation.
- bash: Execute shell commands. Prefer grep/find/ls when those tools are available.
- edit: Make precise file edits with exact text replacement. Multiple edits can be batched.
- write: Create or overwrite files. Auto-creates parent directories.
- grep: Search file contents using regex patterns. Respects .gitignore.
- find: Find files matching a name pattern in a directory tree.
- ls: List directory contents with file metadata.

Guidelines:
- Use bash for file operations if grep/find/ls are not available, otherwise prefer the specialized tools
- Be concise in your responses
- Show file paths clearly when working with files
- Read files before editing them to understand current content
- When editing, make minimal, precise changes

Pi documentation available at: /path/to/pi/README.md
Examples: /path/to/pi/examples/

[Loaded skills metadata: /skill:react-testing - React component testing patterns]

Current date: 2026-05-01
Current working directory: /Users/alice/projects/myapp
```

Notice: identity + tool catalog + behavioral rules + project context + operational context. Clean, layered, readable.
