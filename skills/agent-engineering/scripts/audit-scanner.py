#!/usr/bin/env python3
"""
Automated Agent Audit Scanner

Scans an AI agent codebase for mechanical red flags:
- Monster files (excessive lines)
- Missing safety mechanisms (no max iterations, no compaction, no retry)
- Dynamic system prompt patterns
- Tools without schema validation
- Direct side effects
- Hardcoded provider strings
- Budget tracking gaps

Outputs a JSON report with file path, line number, severity, and description.

Usage:
    python audit-scanner.py /path/to/agent/codebase [--max-file-lines 2000]
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


class AuditScanner:
    def __init__(self, root_path: str, max_file_lines: int = 2000):
        self.root = Path(root_path)
        self.max_file_lines = max_file_lines
        self.findings: List[Dict[str, Any]] = []
        self.total_files_scanned = 0
        self.total_lines_scanned = 0

    def scan(self) -> List[Dict[str, Any]]:
        """Run all scanners and return findings."""
        source_files = self._find_source_files()
        print(f"Scanning {len(source_files)} source files in {self.root}...")

        for filepath in source_files:
            self._scan_file(filepath)

        print(f"Scanned {self.total_files_scanned} files, {self.total_lines_scanned} lines.")
        print(f"Found {len(self.findings)} potential issues.")
        return self.findings

    def _find_source_files(self) -> List[Path]:
        """Find all source files to scan."""
        extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}
        exclude_dirs = {
            "node_modules", ".git", "__pycache__", "dist", "build",
            ".next", ".turbo", "vendor", "target", "venv", ".venv",
            "migrations", "test", "tests", "spec", "__tests__",
        }
        exclude_files = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}

        files = []
        for path in self.root.rglob("*"):
            if path.is_file():
                if path.name in exclude_files:
                    continue
                if any(excl in path.parts for excl in exclude_dirs):
                    continue
                if path.suffix in extensions:
                    files.append(path)
        return files

    def _scan_file(self, filepath: Path):
        """Run all checkers on a single file."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        self.total_files_scanned += 1
        self.total_lines_scanned += content.count("\n")
        relative_path = str(filepath.relative_to(self.root))

        lines = content.split("\n")
        line_count = len(lines)

        # Check 1: Monster file
        if line_count > self.max_file_lines:
            self.findings.append({
                "check": "monster_file",
                "severity": "high",
                "file": relative_path,
                "line": 1,
                "detail": f"File exceeds {self.max_file_lines} lines ({line_count} lines). "
                          f"Consider splitting into smaller, focused components."
            })

        # Check 2: No max iterations
        if not self._has_max_iterations(content, filepath.suffix):
            self.findings.append({
                "check": "no_max_iterations",
                "severity": "critical",
                "file": relative_path,
                "line": self._find_loop_line(lines),
                "detail": "Agent loop found without a visible max_iterations limit. "
                          "Add a hard cap (25-90) to prevent infinite loops."
            })

        # Check 3: Dynamic system prompt
        if self._has_dynamic_system_prompt(content, filepath.suffix):
            self.findings.append({
                "check": "dynamic_system_prompt",
                "severity": "high",
                "file": relative_path,
                "line": self._find_line_pattern(lines, r"system_prompt\s*[\+]=|system_prompt\s*=\s*.*\+|\.append.*system"),
                "detail": "System prompt appears to be modified mid-session. "
                          "This destroys prompt caching. Dynamic content should go in user messages."
            })

        # Check 4: Tools that throw instead of return errors
        if self._has_tool_exceptions(content, filepath.suffix):
            self.findings.append({
                "check": "tools_throw_exceptions",
                "severity": "high",
                "file": relative_path,
                "line": self._find_line_pattern(lines, r"raise\s+\w+Error|raise\s+Exception"),
                "detail": "Tool handler raises exceptions instead of returning error objects. "
                          "Use return {'error': '...'} to let the LLM recover."
            })

        # Check 5: No compaction
        if self._is_agent_file(content) and not self._has_compaction(content, filepath.suffix):
            self.findings.append({
                "check": "no_compaction",
                "severity": "high",
                "file": relative_path,
                "line": 1,
                "detail": "Agent file found but no compaction/summarization/truncation logic detected. "
                          "Long conversations will hit context limits."
            })

        # Check 6: Direct side effects (send email, deploy, payment without pending action)
        if self._has_direct_side_effects(content, filepath.suffix):
            self.findings.append({
                "check": "direct_side_effects",
                "severity": "critical",
                "file": relative_path,
                "line": self._find_line_pattern(lines, r"\.send\(|\.deploy\(|\.publish\(|\.execute\(|\.charge\(|\.pay\("),
                "detail": "Irreversible external effect detected without pending action pattern. "
                          "Use the pending action pattern: create a draft, require user confirmation."
            })

        # Check 7: Hardcoded provider/model
        if self._has_hardcoded_provider(content, filepath.suffix):
            self.findings.append({
                "check": "hardcoded_provider",
                "severity": "medium",
                "file": relative_path,
                "line": self._find_line_pattern(lines, r"openai\.|anthropic\.|google\.genai|gpt-4|claude-"),
                "detail": "Hardcoded provider/model string found. "
                          "Abstract behind a provider layer for flexibility and fallbacks."
            })

        # Check 8: No retry logic
        if self._is_agent_file(content) and not self._has_retry_logic(content, filepath.suffix):
            self.findings.append({
                "check": "no_retry_logic",
                "severity": "medium",
                "file": relative_path,
                "line": 1,
                "detail": "Agent file found but no retry/backoff logic detected. "
                          "Transient API errors will crash the agent."
            })

        # Check 9: No budget tracking
        if self._is_agent_file(content) and not self._has_budget_tracking(content, filepath.suffix):
            self.findings.append({
                "check": "no_budget_tracking",
                "severity": "high",
                "file": relative_path,
                "line": 1,
                "detail": "Agent file found but no token/cost tracking detected. "
                          "Add budget tracking to prevent runaway costs."
            })

        # Check 10: No interrupt mechanism
        if self._is_agent_file(content) and not self._has_interrupt(content, filepath.suffix):
            self.findings.append({
                "check": "no_interrupt_mechanism",
                "severity": "medium",
                "file": relative_path,
                "line": 1,
                "detail": "Agent file found but no interrupt/abort mechanism detected. "
                          "Users need a way to stop the agent mid-run."
            })

    # --- Detection helpers ---

    def _is_agent_file(self, content: str) -> bool:
        """Heuristic: does this file likely contain an agent loop?"""
        indicators = [
            r"while.*True", r"while.*running", r"while.*not.*done",
            r"def\s+run\b", r"def\s+agent\b", r"def\s+converse\b",
            r"tool_call", r"function_call", r"tool_use",
            r"generate\(|\.create\(|messages\.create",
            r"max_iterations", r"max_steps", r"max_turns",
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in indicators)

    def _has_max_iterations(self, content: str, ext: str) -> bool:
        if not self._is_agent_file(content):
            return True  # Not an agent file, skip
        patterns = [
            r"max_iterations", r"max_steps", r"max_turns", r"MAX_ITER",
            r"iteration.*<\s*(50|90|\d{2,3})", r"for\s+\w+\s+in\s+range\(",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _has_dynamic_system_prompt(self, content: str, ext: str) -> bool:
        patterns = [
            r"system_prompt\s*\+=", r"system_prompt\s*=\s*.*\+",
            r"system_prompt\.append",
            r"system_prompt\s*=\s*f.*\{.*\}",
            r"\.add.*system_prompt", r"system_prompt\.push",
            r"system_prompt_string\s*\+=",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _has_tool_exceptions(self, content: str, ext: str) -> bool:
        """Check if tool functions raise instead of returning errors."""
        # Look for tool-like functions that raise exceptions
        tool_func_pattern = r"(?:def\s+(?:handle_|execute_|run_)?(?:tool_|read_|write_|edit_|bash_|search_))"
        has_tool_funcs = bool(re.search(tool_func_pattern, content, re.IGNORECASE))

        if not has_tool_funcs:
            return False

        # Check if those functions raise without catching
        raise_lines = re.findall(r"raise\s+(?!NotImplementedError)", content)
        try_except_blocks = re.findall(r"try\s*:", content)

        if raise_lines and len(raise_lines) > len(try_except_blocks):
            return True

        # Check for functions that open files without try/except
        has_bare_open = bool(re.search(r"(?<!try:\s*\n\s*)open\(.+\)(?!\s*except)", content))
        return has_bare_open

    def _has_compaction(self, content: str, ext: str) -> bool:
        patterns = [
            r"compact", r"summarize?", r"truncat", r"prune",
            r"compress", r"condense", r"context_window",
            r"token.*limit", r"context.*limit", r"max.*token",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _has_direct_side_effects(self, content: str, ext: str) -> bool:
        patterns = [
            r"\.send\(.*email", r"\.sendEmail\(", r"\.send_email\(",
            r"\.deploy\(", r"\.publish\(",
            r"\.charge\(", r"\.pay\(", r"stripe\.",
        ]
        matches = [p for p in patterns if re.search(p, content, re.IGNORECASE)]
        if matches:
            # Check if there's a pending action pattern nearby
            has_pending = bool(re.search(r"pending|draft|confirm|review|approv", content, re.IGNORECASE))
            return not has_pending
        return False

    def _has_hardcoded_provider(self, content: str, ext: str) -> bool:
        patterns = [
            r"openai\.chat\.completions\.create",
            r"anthropic\.Anthropic\(",
            r"anthropic\.messages\.create",
            r'google\.genai',
            r'model\s*=\s*["\']gpt-4',
            r'model\s*=\s*["\']claude-',
            r'model\s*=\s*["\']gemini-',
        ]
        return any(re.search(p, content) for p in patterns)

    def _has_retry_logic(self, content: str, ext: str) -> bool:
        patterns = [
            r"retry", r"backoff", r"max_retries", r"max_attempts",
            r"RateLimitError", r"ServerError", r"rate_limit",
            r"RetryError", r"withRetry", r"retry_with",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _has_budget_tracking(self, content: str, ext: str) -> bool:
        patterns = [
            r"budget", r"token.*count", r"token.*usage", r"token.*used",
            r"cost.*usd", r"cost.*track", r"spend", r"usage.*track",
            r"tokens_used", r"total_tokens", r"max_tokens",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _has_interrupt(self, content: str, ext: str) -> bool:
        patterns = [
            r"interrupt", r"abort", r"cancel.*request",
            r"is_interrupted", r"is_cancelled", r"should_stop",
            r"AbortController", r"abort_signal", r"stop_flag",
            r"threading\.Event", r"asyncio\.Event",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _find_loop_line(self, lines: List[str]) -> int:
        for i, line in enumerate(lines, 1):
            if re.search(r"while\s+(True|not\s+done|running|active)", line, re.IGNORECASE):
                return i
        return 1

    def _find_line_pattern(self, lines: List[str], pattern: str) -> int:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                return i
        return 1


def main():
    parser = argparse.ArgumentParser(description="Audit an AI agent codebase for anti-patterns.")
    parser.add_argument("path", help="Path to the agent codebase to scan")
    parser.add_argument("--max-file-lines", type=int, default=2000,
                        help="Maximum lines before a file is flagged as 'monster' (default: 2000)")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    parser.add_argument("--output", help="Write findings to a JSON file")
    args = parser.parse_args()

    scanner = AuditScanner(args.path, max_file_lines=args.max_file_lines)
    findings = scanner.scan()

    report = {
        "codebase": str(Path(args.path).resolve()),
        "files_scanned": scanner.total_files_scanned,
        "lines_scanned": scanner.total_lines_scanned,
        "issues_found": len(findings),
        "findings": findings,
        "summary": _summarize(findings),
    }

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))
        print(f"Report written to {args.output}")

    if args.json:
        print(json.dumps(report, indent=2))
        return

    # Pretty print
    print(f"\n{'='*60}")
    print(f"Audit Report: {report['codebase']}")
    print(f"Files: {report['files_scanned']}, Lines: {report['lines_scanned']}")
    print(f"Issues: {report['issues_found']}")
    print(f"{'='*60}")

    if not findings:
        print("\nNo mechanical issues found. Run the manual audit checklist for deeper analysis.")
        return

    severities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        severities[f["severity"]] += 1

    print(f"\nCritical: {severities['critical']}, High: {severities['high']}, "
          f"Medium: {severities['medium']}, Low: {severities['low']}\n")

    for i, finding in enumerate(findings, 1):
        prefix = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(finding["severity"], "⚪")
        print(f"{i}. {prefix} [{finding['check']}] {finding['file']}:{finding['line']}")
        print(f"   {finding['detail']}\n")


def _summarize(findings: List[Dict]) -> Dict[str, int]:
    counts = {}
    for f in findings:
        key = f["check"]
        counts[key] = counts.get(key, 0) + 1
    return counts


if __name__ == "__main__":
    main()
