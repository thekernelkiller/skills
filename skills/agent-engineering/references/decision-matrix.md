# Decision Matrix: Architecture Choices for AI Agents

When you're building a new agent or refactoring an existing one, work through these decisions in order.

---

## 1. Loop: Build vs Use SDK

| Factor | Build Your Own Loop | Use an SDK (Vercel AI, LangChain, etc.) |
|--------|-------------------|----------------------------------------|
| **Control** | Full control over caching, retries, parallel execution | Limited to SDK's abstractions |
| **Code** | ~200 lines of core loop | ~20 lines of setup |
| **Maintenance** | You own the bugs | SDK team fixes bugs |
| **Customization** | Unlimited | Must work within SDK's model |
| **Lock-in** | None | Locked to SDK's API and update cycle |
| **Learning curve** | Need to understand the loop pattern | Need to learn the SDK's API |

**Recommendation**: Build your own loop for production agents. The 200-line investment pays off in control and flexibility. Use an SDK for prototypes and MVPs where speed matters more than control.

---

## 2. Provider Strategy: Direct vs Abstraction Layer

| Factor | Direct API Calls | Abstraction Layer |
|--------|-----------------|-------------------|
| **Setup** | Trivial for one provider | Moderate effort for the adapter |
| **Multi-provider** | Rewrite for each provider | Add one adapter file per provider |
| **Fallback** | Manual retry with different client | Automatic fallback chain |
| **Testing** | Need real API keys | Mock the adapter, test without API |
| **Cost optimization** | Manual | Automatic model selection by task |

**Recommendation**: Always build a thin abstraction layer. It's 2-3 files. The ability to switch providers, add fallbacks, and test without API keys pays for itself immediately.

---

## 3. Tool Registration: Explicit vs Self-Registering

| Factor | Explicit Registry | Self-Registration |
|--------|------------------|-------------------|
| **Simplicity** | Very simple, obvious | More complex discovery mechanism |
| **Tool count <10** | Perfect | Overkill |
| **Tool count 10-50** | Manageable but tedious | Ideal — zero boilerplate |
| **Tool count 50+** | Unwieldy | Necessary |
| **Plugin system** | Extensions must modify registry | Extensions just add files |

**Recommendation**: Start with explicit registry. Switch to self-registration when you have >10 tools or need a plugin system.

---

## 4. Parallel Execution: Always vs Analyzed

| Factor | Always Parallel | Always Sequential | Safety Analyzed |
|--------|----------------|-------------------|-----------------|
| **Speed** | Fastest | Slowest | Fast but safe |
| **Safety** | Unsafe — can corrupt files | Safe | Safe |
| **Complexity** | Simple | Simple | Moderate |
| **File mutations** | Race conditions | No races | No races |

**Recommendation**: Always implement safety analysis. It's ~50 lines of code. Parallelize read-only tools and mutation tools on different files. Serialize mutations on the same file. Never parallelize interactive tools.

---

## 5. Prompt Architecture: Monolithic vs Layered

| Factor | Monolithic | Layered |
|--------|-----------|---------|
| **Readability** | Hard to understand what goes where | Clear boundaries between concerns |
| **Modifiability** | Change anything, risk breaking everything | Change one layer, others unaffected |
| **Debugging** | "Which part of this 2000-line string caused the issue?" | "The behavioral rules layer is the issue" |
| **Caching** | Can still freeze (but harder to verify) | Easy to verify frozen layers |

**Recommendation**: Always use layered. It costs nothing and pays for itself the first time you need to debug the prompt.

---

## 6. Memory: Built-in vs External vs None

| Factor | Built-in | External Plugin | No Memory |
|--------|---------|----------------|-----------|
| **Simplicity** | Simple key-value store | Complex, external dependency | Simplest |
| **Capability** | Basic facts | Semantic search, user modeling | None |
| **Overhead** | SQLite, ~100 lines | External service, API keys | Zero |
| **Privacy** | All data local | Data sent to third party | No data stored |

**Recommendation**: Start with no memory. Add built-in memory (simple key-value store, injected into user messages) when users ask for it. Add external memory plugins only if built-in is insufficient and users accept the privacy tradeoff.

---

## 7. Extensibility: Fixed vs Plugin System

| Factor | Fixed | Plugin System |
|--------|-------|---------------|
| **Complexity** | Simple, no extension API | Significant API design and maintenance |
| **When needed** | Single-team codebase, controlled environment | Platform with third-party developers |
| **Cost** | Zero | Ongoing maintenance of extension API stability |

**Recommendation**: Start fixed. Add a plugin system ONLY when third parties need to extend the agent. Never pre-build extensibility "just in case." The extension API will be wrong because you haven't seen how people want to extend it.

---

## 8. Safety: Which Layers to Implement

| Layer | When to Add | Priority |
|-------|------------|----------|
| Prompt hardening | Immediately if processing external content | HIGH |
| Tool guardrails (rate limits) | Before production deployment | HIGH |
| Approval gates | Before destructive tools exist | HIGH |
| Pending actions | Before irreversible side effects exist | CRITICAL |
| Budget tracking | Before users can spend money | HIGH |

**Recommendation**: Implement ALL five layers before any user can interact with the agent. Safety is not progressive — it's binary. Either the agent is safe or it isn't.

---

## 9. Scale: Single File vs Monorepo

| Factor | Single File | Monorepo |
|--------|------------|----------|
| **When** | Prototype, personal tool, <5 tools | Production, multiple platforms, plugins |
| **Complexity** | Minimal | Significant build/dev tooling |
| **Deployment** | Copy one file | Build pipeline, dependencies |
| **Team size** | 1-2 | 3+ |
| **Refactoring to monorepo** | Easy if concerns are separated early | N/A |

**Recommendation**: Start with a single-file prototype. Separate concerns into files when the file exceeds 500 lines. Move to packages when you have multiple platforms or independent deployable units. The key is separating concerns EARLY — even in a single file, keep the loop, tools, prompts, and safety in clearly separated sections.

---

## 10. Domain: General-Purpose vs Specialized

| Factor | General-Purpose | Domain-Specific |
|--------|----------------|-----------------|
| **Tool set** | Broad (file ops, web, terminal, etc.) | Deep (domain-specific: email, code, data) |
| **System prompt** | Generic, adaptable | Domain-specific, includes domain safety rules |
| **Safety** | Standard (don't delete files) | Domain-specific (don't send email without confirmation) |
| **Example** | Claude Code, Cursor, OpenCode | inbox-zero, Devin, GitHub Copilot |

**Recommendation**: Start specialized. It's easier to add general capabilities to a domain-specific agent than to specialize a general agent. The system prompt and safety rules benefit enormously from domain focus.

---

## Quick Decision Tree

```
Are you building from scratch or auditing?
  ├── From scratch → Start with a 200-line ReAct loop
  │   ├── <10 tools → Explicit registry
  │   ├── 10-50 tools → Switch to self-registration
  │   └── 50+ tools → Add composable toolsets
  │
  └── Auditing existing → Run audit-scanner.py first
      ├── Missing safety? → Add safety layers BEFORE anything else
      ├── No compaction? → Add compaction next
      ├── Dynamic system prompt? → Freeze it, move dynamic content to user messages
      └── Monster class? → Refactor when you next add a feature (opportunistic refactoring)
```
