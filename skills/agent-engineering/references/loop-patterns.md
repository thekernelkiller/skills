# Agent Loop Patterns: Detailed Implementation Guide

This reference provides detailed pseudocode and implementation notes for the four agent loop variants, interrupt mechanisms, retry strategies, and budget tracking.

---

## Variant 1: Flat Loop (hermes-agent style)

The simplest and most common pattern. One loop, complete control.

```python
class Agent:
    def __init__(self, model, tools, system_prompt):
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        self.conversation = [{"role": "system", "content": system_prompt}]
        self.max_iterations = 90
        self.is_interrupted = threading.Event()
        self.tokens_used = 0
        self.max_budget_tokens = 200_000

    def run(self, user_message: str) -> str:
        self.conversation.append({"role": "user", "content": user_message})
        iteration = 0

        while iteration < self.max_iterations:
            if self.is_interrupted.is_set():
                return "Interrupted by user."
            if self.tokens_used >= self.max_budget_tokens:
                return "Budget exhausted."

            response = self._llm_call_with_retry()
            self.tokens_used += response.usage.total_tokens

            if not response.tool_calls:
                self.conversation.append({"role": "assistant", "content": response.text})
                return response.text

            tool_calls = self._analyze_parallel_safety(response.tool_calls)
            for call in tool_calls:
                result = self.tools.execute(call.name, call.args)
                self.conversation.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

            iteration += 1

        return f"Max iterations ({self.max_iterations}) reached."

    def interrupt(self):
        self.is_interrupted.set()

    def _analyze_parallel_safety(self, tool_calls):
        """Group tool calls into parallel-safe batches."""
        # Extract affected resources (file paths, URLs, etc.)
        # Check for overlaps → split batches
        # Read-only tools can always parallelize
        # Mutation tools need serialization on same file
        pass
```

**When to use**: You want complete control over the loop. Direct API calls, no SDK abstraction. Building a general-purpose agent.

**Pros**: Simple, debuggable, no framework lock-in.
**Cons**: You write the retry logic, parallel analysis, and budget tracking yourself.

---

## Variant 2: Nested Loop (pi-mono style)

Two loops: outer processes follow-up messages, inner processes tool calls. Steering messages can interrupt the inner loop.

```python
class NestedLoopAgent:
    def __init__(self):
        self.steering_queue = []      # Interrupt current work
        self.followup_queue = []      # Process after current work
        self.inner_max_iterations = 50
        self.conversation = []
        self.currently_streaming = False

    async def run_loop(self):
        while True:
            # OUTER LOOP: handle follow-up messages
            steering, followup = self._drain_queues()
            
            if not steering and not followup and not self._has_pending_work():
                break

            # INNER LOOP: process steering + original work
            iteration = 0
            while iteration < self.inner_max_iterations:
                # Drain any new steering messages
                new_steering, _ = self._drain_queues()
                if new_steering:
                    self.conversation.extend(new_steering)
                    iteration = 0  # Reset counter after steer

                response = await self._llm_call()
                
                if not response.tool_calls:
                    self.conversation.append(response)
                    break

                await self._execute_tools_parallel(response.tool_calls)
                iteration += 1

            # Process follow-up messages for next outer iteration
            if followup:
                self.conversation.extend(followup)
            else:
                break

    def steer(self, message: str):
        """Inject immediately — interrupts current inner loop."""
        self.steering_queue.append({"role": "user", "content": message})

    def follow_up(self, message: str):
        """Process after current work completes."""
        self.followup_queue.append({"role": "user", "content": message})

    def _drain_queues(self):
        steering = list(self.steering_queue)
        followup = list(self.followup_queue)
        self.steering_queue.clear()
        self.followup_queue.clear()
        return steering, followup
```

**When to use**: Interactive agents where users want to course-correct without aborting. The steering mechanism is the key innovation — it lets users inject "actually, use PostgreSQL not MySQL" mid-task and the agent adapts without losing context.

**Queue modes**: 
- `"all"`: Drain everything in one go. Good for batch corrections.
- `"one-at-a-time"`: Process one message per turn. Good for step-by-step guidance.

---

## Variant 3: SDK-Driven Loop (inbox-zero style)

Delegate the loop to a library. Focus on tools and prompts.

```typescript
import { tool, generateText } from "ai";

const myTools = {
  read_file: tool({
    description: "Read the contents of a file",
    parameters: z.object({ path: z.string() }),
    execute: async ({ path }) => ({ content: await fs.readFile(path, "utf-8") }),
  }),
  // ... more tools
};

const response = await generateText({
  model: myModel,
  system: systemPrompt,
  messages: conversation,
  tools: myTools,
  maxSteps: 25,             // This IS the iteration limit
  maxTokens: 100_000,       // Budget
  toolChoice: "auto",
});
```

**When to use**: You want to focus on tools and prompts, not infrastructure. The SDK handles the loop, retries, parallel execution, and streaming.

**Pros**: Less code, battle-tested loop, automatic parallel execution.
**Cons**: Less control over caching strategy, interrupt mechanism, and budget granularity. Framework lock-in.

**Key SDK abstractions**:
- `maxSteps`: The iteration limit (equivalent to max_iterations)
- `maxTokens`: Total token budget across all steps
- `toolChoice: "auto"`: The model decides when to use tools
- `onStepFinish`: Callback for logging, budget tracking, compaction triggers

---

## Variant 4: Event-Driven Loop (pi-mono's extension architecture)

The loop is simple. Extensibility comes from events.

```typescript
class EventDrivenAgent {
    private listeners = new Map<AgentEvent, Listener[]>();

    async run(userMessage: string): Promise<void> {
        this.emit("agent_start");
        
        await this.emit("turn_start");
        this.emit("message_start", { role: "user", content: userMessage });
        
        let response = await this.emit("before_llm_call").then(() => this._llmCall());
        await this.emit("after_llm_call", response);
        
        if (response.toolCalls) {
            for (const call of response.toolCalls) {
                this.emit("tool_execution_start", call);
                const result = await this.tools.execute(call);
                this.emit("tool_execution_end", { call, result });
            }
            // Continue inner loop...
        }
        
        this.emit("turn_end");
        this.emit("agent_end");
    }

    subscribe(event: AgentEvent, listener: Listener): void {
        this.listeners.get(event)?.push(listener);
    }

    private emit(event: AgentEvent, data?: any): void {
        for (const listener of this.listeners.get(event) || []) {
            listener(data);
        }
    }
}
```

**When to use**: Platform agents where third parties build plugins. The event system lets extensions hook into any lifecycle point without modifying the core loop.

**Events typically supported**:
- `agent_start`, `agent_end` — session lifecycle
- `turn_start`, `turn_end` — per-turn boundaries
- `message_start`, `message_end` — each message added to transcript
- `tool_execution_start`, `tool_execution_end` — tool lifecycle
- `before_llm_call`, `after_llm_call` — LLM interaction hooks
- `context_transform` — modify context before LLM call
- `session_compact`, `session_fork` — context management events

---

## Interrupt Mechanism

Every agent needs a way to stop mid-run. The pattern:

```python
import threading

class InterruptibleAgent:
    def __init__(self):
        self._interrupted = threading.Event()

    def run(self, message: str):
        while not self._interrupted.is_set():
            if self._interrupted.is_set():
                self._cleanup()
                return {"status": "interrupted", "partial_results": self.results}


            response = self._llm_call()
            
            for tool_call in response.tool_calls:
                if self._interrupted.is_set():
                    break
                
                # Long-running tools should also check
                result = self.tools.execute(tool_call, interrupt_flag=self._interrupted)
                # ...

    def interrupt(self):
        self._interrupted.set()

    def _cleanup(self):
        # Kill any running subprocesses
        # Close open file handles
        # Persist partial conversation
        pass
```

**Key design decisions**:
- Thread-safe flag (Python `threading.Event`, JavaScript `AbortController`)
- Checked at loop top AND during long tool operations
- Cleanup on interrupt (kill subprocesses, persist partial transcript)
- Tools that take >1 second should accept and check an interrupt flag

---

## Retry Strategy

LLM APIs fail. A lot. The retry envelope:

```python
import time
import random

def llm_call_with_retry(model, messages, max_retries=3, fallback_models=None):
    attempt = 0
    models_to_try = [model] + (fallback_models or [])
    
    for current_model in models_to_try:
        for attempt in range(max_retries):
            try:
                response = current_model.generate(messages)
                return response
                
            except RateLimitError as e:
                wait = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff + jitter
                time.sleep(wait)
                
            except ServerError as e:
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                
            except ContextOverflowError:
                compact_conversation(messages)  # Must compact before retrying
                continue
                
            except AuthError:
                raise  # Don't retry auth errors
    
    raise AgentError("All retries exhausted across all models")
```

**Error classification**:
- **Rate limit (429)**: Retry with backoff. Switch to fallback model.
- **Server error (503, 500)**: Retry with backoff.
- **Context overflow**: Compact, then retry. Never retry without compacting first.
- **Auth error (401, 403)**: Fail immediately. Don't retry.
- **Timeout**: Retry with longer timeout or switch to faster model.
- **Bad request (400)**: Fail immediately. Something is wrong with the request.

**Fallback model chains**: `anthropic:claude-sonnet-4-20250514,openai:gpt-4o,google:gemini-2.5-pro`. A simple comma-separated list of `provider:model` pairs. Try each in order.

---

## Budget Tracking

```python
class BudgetTracker:
    def __init__(self, max_tokens=200_000, max_cost_usd=5.00):
        self.max_tokens = max_tokens
        self.max_cost_usd = max_cost_usd
        self.tokens_used = 0
        self.cost_usd = 0.0
        self.pricing = {
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},  # per 1M tokens
            "gpt-4o": {"input": 2.50, "output": 10.00},
        }

    def record_usage(self, model: str, input_tokens: int, output_tokens: int):
        self.tokens_used += input_tokens + output_tokens
        pricing = self.pricing.get(model, {"input": 5.00, "output": 15.00})
        self.cost_usd += (input_tokens / 1_000_000) * pricing["input"]
        self.cost_usd += (output_tokens / 1_000_000) * pricing["output"]

    def is_exhausted(self) -> bool:
        return self.tokens_used >= self.max_tokens or self.cost_usd >= self.max_cost_usd

    def usage_report(self) -> str:
        return f"Tokens: {self.tokens_used}/{self.max_tokens}, Cost: ${self.cost_usd:.2f}/{self.max_cost_usd:.2f}"
```

**Model usage guard** (inbox-zero's pattern): When weekly spend exceeds a limit, force-switch all agents to the cheapest model tier. This prevents surprise bills without manual intervention.

---

## Putting It All Together

A complete, minimal agent with all the patterns:

```python
class MinimalAgent:
    def __init__(self, model, tools, system_prompt, max_iterations=50, max_tokens=200_000):
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.budget = BudgetTracker(max_tokens=max_tokens)
        self.conversation = [{"role": "system", "content": system_prompt}]
        self._interrupted = threading.Event()
        self.fallback_models = []

    def run(self, user_message: str) -> str:
        self.conversation.append({"role": "user", "content": user_message})
        
        for iteration in range(self.max_iterations):
            # Check exits
            if self._interrupted.is_set():
                return "Interrupted."
            if self.budget.is_exhausted():
                return f"Budget exhausted. {self.budget.usage_report()}"

            # LLM call with retry
            response = self._call_with_retry()
            self.budget.record_usage(
                self.model.name, 
                response.usage.input_tokens, 
                response.usage.output_tokens
            )

            # No tool calls → done
            if not response.tool_calls:
                self.conversation.append({"role": "assistant", "content": response.text})
                return response.text

            # Execute tools
            for call in self._parallelize(response.tool_calls):
                result = self.tools.execute(call.name, call.args)
                self.conversation.append({
                    "role": "tool", 
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

        return f"Max iterations ({self.max_iterations}) reached."

    def interrupt(self):
        self._interrupted.set()
```

This is ~40 lines of core logic. The rest of any production agent is tools, safety, compaction, and UX — not the loop.
