# Tool System Design: Patterns, Validation, and Best Practices

## Tool Registration Patterns

### Pattern 1: Explicit Registry (simplest)

Best for agents with <10 tools. No magic. Clear and debuggable.

```python
TOOLS = {
    "read_file": {
        "description": "Read the contents of a file at the given path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read"},
                "offset": {"type": "integer"},
                "limit": {"type": "integer"}
            },
            "required": ["path"]
        },
        "handler": read_file_handler,
    },
    "write_file": {
        "description": "Create or overwrite a file with the given content.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        },
        "handler": write_file_handler,
    },
}

def get_tool_definitions():
    return [{"type": "function", "function": {"name": name, **rest}} 
            for name, rest in TOOLS.items()]

def execute_tool(name: str, args: dict):
    tool = TOOLS[name]
    validate_args(args, tool["parameters"])
    return tool["handler"](**args)
```

### Pattern 2: Closure Factory

Best when tools need runtime context (database connections, API clients, user identity).

```typescript
function createEmailTools(ctx: { provider: EmailProvider; userId: string }) {
  return {
    searchInbox: tool({
      description: "Search the user's inbox. Use Gmail search syntax.",
      parameters: z.object({
        query: z.string().describe("Gmail search query. e.g., 'from:alice newer_than:7d'"),
        maxResults: z.number().optional().default(10),
      }),
      execute: async ({ query, maxResults }) => {
        const emails = await ctx.provider.search(ctx.userId, query, maxResults);
        return { count: emails.length, emails };
      },
    }),
    readEmail: tool({
      description: "Read the full content of an email by its ID.",
      parameters: z.object({
        emailId: z.string().describe("The email's unique identifier"),
      }),
      execute: async ({ emailId }) => {
        return await ctx.provider.getEmail(ctx.userId, emailId);
      },
    }),
  };
}
```

The closure captures `ctx.provider` and `ctx.userId`. When the tool executes, it has access to the current database connection without global state. This is dependency injection for tools.

### Pattern 3: Self-Registration with AST Discovery (hermes-agent style)

Best for plugin systems with many tools. Each tool file calls `register()` at module level. An AST scanner finds and imports all tool files automatically.

```python
# tools/file_tools.py
from tools.registry import registry

def _handle_read_file(args, task_id=None):
    path = resolve_abs_path(args["path"])
    with open(path) as f:
        content = f.read()
    return json.dumps({"path": path, "content": content[:100000]})

registry.register(
    name="read_file",
    toolset="file",
    schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to read"},
            "offset": {"type": "integer"},
            "limit": {"type": "integer"}
        },
        "required": ["path"]
    },
    handler=_handle_read_file,
    check_fn=lambda: True,  # Always available
    max_result_size_chars=100_000,
)

# tools/registry.py
import ast
import importlib
import os

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, toolset, schema, handler, check_fn=None, **meta):
        self._tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
            "check_fn": check_fn or (lambda: True),
            **meta
        }

    def discover_builtin_tools(self, tools_dir: str):
        """Scan tools/ directory for files with registry.register() calls."""
        for filename in os.listdir(tools_dir):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue
            filepath = os.path.join(tools_dir, filename)
            with open(filepath) as f:
                tree = ast.parse(f.read())
            
            # Check if file has top-level registry.register() call
            has_register = any(
                isinstance(node, ast.Expr) and
                isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Attribute) and
                node.value.func.attr == "register"
                for node in ast.iter_child_nodes(tree)
            )
            
            if has_register:
                module_name = f"tools.{filename[:-3]}"
                importlib.import_module(module_name)

    def get_definitions(self, tool_names: list[str]):
        """Return OpenAI-format tool definitions for the given tool names."""
        return [
            {"type": "function", "function": {
                "name": name,
                "description": self._tools[name]["schema"].get("description", ""),
                "parameters": self._tools[name]["schema"],
            }}
            for name in tool_names
            if name in self._tools and self._tools[name]["check_fn"]()
        ]

    def dispatch(self, name: str, args: dict) -> str:
        tool = self._tools[name]
        validated = self._validate_and_coerce(args, tool["schema"])
        return tool["handler"](validated)
```

To add a new tool: create a `.py` file, call `registry.register()`, done. No import lists, no config files, no manual registration.

### Pattern 4: Dual-Layer (pi-mono style)

Separate the rich tool definition (UI, prompts) from the lean execution contract (agent loop). The two layers are connected by an adapter.

```typescript
// --- Layer 1: Rich Tool Definition (for UI, prompts, rendering) ---

interface ToolDefinition<TParams, TDetails> {
  name: string;
  label: string;                    // Human-readable name
  description: string;              // Full description for the LLM
  parameters: TSchema<TParams>;     // TypeBox schema
  promptSnippet: string;            // One-line for system prompt
  promptGuidelines: string[];       // Bullets for system prompt
  execute(args: TParams, ops: ToolOperations): Promise<ToolResult<TDetails>>;
  
  // TUI rendering (optional)
  renderCall?(args: TParams): string;              // Preview while streaming
  renderResult?(result: TDetails): string;          // Formatted output
  renderShell?: boolean;                            // Show inline or not
}

const readToolDef: ToolDefinition<ReadArgs, ReadResult> = {
  name: "read",
  label: "Read",
  description: "Reads a file at the given path. Use offset and limit for large files. Supports text and images.",
  parameters: Type.Object({
    path: Type.String({ description: "Path to the file" }),
    offset: Type.Optional(Type.Number()),
    limit: Type.Optional(Type.Number()),
  }),
  promptSnippet: "read: Read file contents at a path. Use offset/limit for large files.",
  promptGuidelines: [
    "Read files before editing them to understand current content",
    "Use offset and limit when reading large files (>500 lines)",
    "Read imge files to check their dimensions before processing",
  ],
  execute: async (args, ops) => {
    const content = await ops.readFile(args.path);
    return { path: args.path, content, truncated: content.length > 100000 };
  },
  renderCall: (args) => `Reading ${args.path}...`,
  renderResult: (result) => `\`\`\`\n${result.content.slice(0, 2000)}\n\`\`\``,
};

// --- Layer 2: Lean Agent Tool (for the loop) ---

interface AgentTool<TParams> {
  label: string;
  parameters: TSchema<TParams>;
  prepareArguments(args: any): TParams;
  execute(args: TParams): Promise<string>;  // Returns JSON string
}

function wrapToolDefinition<TParams, TDetails>(
  def: ToolDefinition<TParams, TDetails>,
  ops: ToolOperations,
): AgentTool<TParams> {
  return {
    label: def.label,
    parameters: def.parameters,
    prepareArguments: (args) => {
      const validated = validateAndCoerce(def.parameters, args);
      return validated;
    },
    execute: async (args) => {
      const result = await def.execute(args, ops);
      return JSON.stringify(result);
    },
  };
}
```

**Why this separation matters**: The agent loop needs `execute(args) → string`. It shouldn't know about syntax highlighting, diff previews, or prompt snippets. The UI layer needs all of those. The adapter pattern lets both concerns evolve independently.

---

## Schema Design Checklist

A good tool schema has these properties:

1. **Descriptive parameter names**: `path`, not `p`. `query`, not `q`. The LLM reads parameter names.
2. **Parameter-level descriptions**: Every parameter has a `description` field in the schema. The LLM uses these to understand what to pass.
3. **Precise types**: `integer`, not `number` if the value is always whole. `string` with `enum` if there are specific valid values.
4. **Sensible defaults**: `offset: { type: "integer", default: 0 }`. Defaults reduce the LLM's cognitive load.
5. **Required vs optional**: Only mark as `required` what's truly required. Optional parameters with defaults give the LLM flexibility.
6. **Constraints**: `minimum`, `maximum`, `minLength`, `maxLength`. These prevent absurd values.

```json
{
  "name": "search_files",
  "description": "Search for files matching a glob pattern in a directory.",
  "parameters": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "Glob pattern to match. e.g., '**/*.py' for all Python files, 'src/**/*.ts' for TS files in src."
      },
      "directory": {
        "type": "string",
        "description": "Directory to search in. Defaults to current working directory.",
        "default": "."
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results to return.",
        "minimum": 1,
        "maximum": 500,
        "default": 50
      }
    },
    "required": ["pattern"]
  }
}
```

---

## Argument Validation and Repair

LLMs produce malformed JSON for tool arguments. A lot. Here's how to handle it:

```python
import json
import re

def repair_and_validate(args_str: str, schema: dict) -> dict:
    """
    Parse, repair, coerce, and validate tool call arguments against a schema.
    Returns validated args dict or raises with error message for the LLM.
    """
    # Step 1: Parse (with repair)
    try:
        args = json.loads(args_str)
    except json.JSONDecodeError:
        args = _repair_json(args_str)
    
    # Step 2: Coerce types based on schema
    args = _coerce_types(args, schema)
    
    # Step 3: Validate against schema
    errors = _validate_against_schema(args, schema)
    if errors:
        raise ValidationError(f"Invalid arguments: {errors}")
    
    return args


def _repair_json(s: str) -> dict:
    """Fix common LLM JSON mistakes."""
    # Remove trailing commas before } or ]
    s = re.sub(r',\s*}', '}', s)
    s = re.sub(r',\s*]', ']', s)
    
    # Replace Python literals
    s = s.replace("None", "null")
    s = s.replace("True", "true")
    s = s.replace("False", "false")
    
    # Fix unescaped control characters in strings
    s = re.sub(r'[\x00-\x1f]', lambda m: f'\\u{ord(m.group(0)):04x}', s)
    
    # Add missing closing braces (if unclosed object)
    open_braces = s.count('{') - s.count('}')
    s += '}' * open_braces
    
    # Add missing closing brackets
    open_brackets = s.count('[') - s.count(']')
    s += ']' * open_brackets
    
    return json.loads(s)


def _coerce_types(args: dict, schema: dict) -> dict:
    """Coerce string values to schema-declared types."""
    properties = schema.get("properties", {})
    for key, value in args.items():
        if key not in properties:
            continue
        prop_type = properties[key].get("type")
        
        if prop_type == "integer" and isinstance(value, str):
            try:
                args[key] = int(value)
            except ValueError:
                pass
        
        elif prop_type == "number" and isinstance(value, str):
            try:
                args[key] = float(value)
            except ValueError:
                pass
        
        elif prop_type == "boolean" and isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                args[key] = True
            elif value.lower() in ("false", "0", "no"):
                args[key] = False
    
    return args
```

Without repair and coercion, ~5-10% of tool calls fail on malformed JSON. With them, failure rate drops to <1%.

---

## Parallel Safety Analysis

```python
def analyze_parallel_safety(tool_calls: list[ToolCall], registry: ToolRegistry) -> list[list[ToolCall]]:
    """
    Split tool calls into batches that can run in parallel.
    Returns list of batches. Each batch runs in parallel.
    Batches run sequentially.
    """
    if len(tool_calls) == 1:
        return [tool_calls]
    
    # Get metadata about each tool call
    resources = []  # List of sets of affected resources
    for call in tool_calls:
        tool_meta = registry.get_metadata(call.name)
        if tool_meta.get("never_parallelize"):
            # This tool must run alone
            return [[call] for call in tool_calls]
        
        affected = _extract_affected_resources(call)
        resources.append(affected)
    
    # Greedy batching: group non-overlapping calls
    batches = []
    used = set()
    
    for i, call in enumerate(tool_calls):
        if i in used:
            continue
        
        batch = [call]
        batch_resources = resources[i].copy()
        
        for j in range(i + 1, len(tool_calls)):
            if j in used:
                continue
            
            # Only parallelize if no resource overlap
            if not batch_resources & resources[j]:
                batch.append(tool_calls[j])
                batch_resources |= resources[j]
                used.add(j)
        
        used.add(i)
        batches.append(batch)
    
    return batches


def _extract_affected_resources(call: ToolCall) -> set[str]:
    """Extract file paths, URLs, etc. that a tool call affects."""
    resources = set()
    
    if call.name in ("read_file", "write_file", "edit_file"):
        path = call.args.get("path", "")
        if path:
            # Normalize to absolute path
            resources.add(os.path.abspath(path))
    
    elif call.name == "web_search":
        # Web searches never conflict
        pass
    
    elif call.name == "clarify":
        # Interactive tools always exclusive
        resources.add("__INTERACTIVE__")
    
    return resources
```

**Key insight**: Read-only tools on different files → parallel. Mutation tools on different files → parallel. Mutation tools on same file → sequential. Interactive tools → always sequential.

---

## Error-as-Result Pattern

Every tool handler must catch ALL exceptions and return structured errors:

```python
def read_file_handler(path: str, offset: int = 0, limit: int = None) -> dict:
    try:
        full_path = resolve_abs_path(path)
        
        if not full_path.exists():
            return {"error": f"File not found: {path}", "path": str(full_path)}
        
        if full_path.is_dir():
            return {"error": f"Path is a directory, not a file: {path}", "path": str(full_path)}
        
        with open(full_path) as f:
            if offset:
                # Seek to offset (expensive but works)
                for _ in range(offset):
                    f.readline()
            
            lines = f.readlines()[:limit] if limit else f.readlines()
            content = "".join(lines)
            is_truncated = len(lines) == limit if limit else len(content) > 100_000
        
        result = {
            "path": str(full_path),
            "content": content[:100_000],
            "total_lines": sum(1 for _ in open(full_path)),
        }
        
        if is_truncated:
            result["truncated"] = True
            result["hint"] = f"Output truncated. Use offset={offset + (limit or 0)} to continue reading."
        
        return result
        
    except PermissionError:
        return {"error": f"Permission denied: {path}"}
    except Exception as e:
        return {"error": f"Unexpected error reading {path}: {str(e)}"}
```

The LLM reads `"error": "File not found: /foo/bar.txt"` and responds with "Let me check the path — maybe it's in `/foo/baz.txt`?" This is vastly better than a crashed loop with a Python traceback.

---

## Pluggable I/O Operations (pi-mono's Innovation)

```typescript
interface ReadOperations {
  readFile(path: string): Promise<string>;
  fileExists(path: string): Promise<boolean>;
  isDirectory(path: string): Promise<boolean>;
}

interface WriteOperations {
  writeFile(path: string, content: string): Promise<void>;
  createDirectory(path: string): Promise<void>;
  deleteFile(path: string): Promise<void>;
}

interface BashOperations {
  exec(command: string, options?: { cwd?: string; timeout?: number }): Promise<{
    stdout: string;
    stderr: string;
    exitCode: number;
  }>;
}

// --- Local implementation ---
const localOps: ReadOperations & WriteOperations & BashOperations = {
  readFile: (path) => fs.promises.readFile(path, "utf-8"),
  writeFile: (path, content) => fs.promises.writeFile(path, content),
  exec: (command, options) => execAsync(command, options),
  // ...
};

// --- SSH implementation (same interface, different implementation) ---
const sshOps: ReadOperations & WriteOperations & BashOperations = {
  readFile: (path) => sshClient.exec(`cat ${path}`).then(r => r.stdout),
  writeFile: (path, content) => sshClient.exec(`cat > ${path}`, { stdin: content }),
  exec: (command, options) => sshClient.exec(command, options),
  // ...
};

// Tools don't know which implementation they're using
const readTool = createReadTool(localOps);   // Local agent
const readTool = createReadTool(sshOps);     // Remote agent
const readTool = createReadTool(testOps);    // Test with mock filesystem
```

The tool code is pure logic. "Where" the tool runs is a configuration concern. This is dependency injection for agent tools.

---

## File Mutation Queue

When parallel tool calls target the same file, serialize access:

```typescript
class FileMutationQueue {
  private queues = new Map<string, Promise<void>>();

  async withLock(path: string, fn: () => Promise<void>): Promise<void> {
    const normalized = path.resolve(path);
    
    // Chain onto the existing lock for this file
    const previous = this.queues.get(normalized) || Promise.resolve();
    const current = previous.then(fn);
    this.queues.set(normalized, current);
    
    await current;
    
    // Cleanup: remove if no more pending
    if (this.queues.get(normalized) === current) {
      this.queues.delete(normalized);
    }
  }
}

// Usage in tool execution:
const queue = new FileMutationQueue();

async function executeToolCalls(calls: ToolCall[]): Promise<void> {
  const promises = calls.map(async (call) => {
    if (call.name === "edit_file" || call.name === "write_file") {
      return queue.withLock(call.args.path, () => editFile(call.args));
    }
    return executeTool(call);  // Read-only tools don't need the lock
  });
  
  await Promise.all(promises);
}
```

This ensures that even when tools run "in parallel," file mutations targeting the same path are serialized.

---

## Tool Result Size Management

Tool results must be capped. 100K characters is a common limit. Truncated results must include actionable hints:

```python
MAX_RESULT_CHARS = 100_000

def cap_result(result: str, tool_name: str, args: dict) -> str:
    if len(result) <= MAX_RESULT_CHARS:
        return result
    
    truncated = result[:MAX_RESULT_CHARS]
    
    # Add a hint based on the tool
    if tool_name == "read_file":
        current_offset = args.get("offset", 0)
        next_offset = current_offset + truncated.count("\n")
        hint = f"\n\n[Output truncated at {MAX_RESULT_CHARS} characters. "
        hint += f"Use offset={next_offset} to continue reading from this point.]"
    
    elif tool_name == "web_search":
        hint = f"\n\n[Results truncated. Narrow your search query for more specific results.]"
    
    elif tool_name == "find":
        hint = f"\n\n[Only first {MAX_RESULT_CHARS} chars shown. Use pattern to narrow results.]"
    
    else:
        hint = f"\n\n[Output truncated at {MAX_RESULT_CHARS} characters.]"
    
    return truncated + hint
```

The hint is critical. Without it, the LLM doesn't know there's more data and makes decisions on incomplete information.
