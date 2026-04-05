## 1. Planning and Re-Planning

* For non-trivial work (3+ steps, cross-file changes, or design tradeoffs), create a concrete plan first.
* Keep exactly one step **in_progress** at a time and update status as you go.
* If new evidence breaks the current approach, stop, revise the plan, and continue from the updated plan.
* Include verification tasks in the plan, not just implementation tasks.
* For complex tasks, write a short spec first: scope, constraints, risks, and acceptance criteria.

---

## 2. Parallel Work Strategy (Codex Equivalent to Subagents)

* Codex does not use “subagents”; use parallel tool calls where safe (**multi_tool_use.parallel**) to speed up discovery.
* Parallelize independent reads/searches/tests (file scans, logs, status checks).
* Keep each parallel task narrowly scoped (one question per call group).
* Synthesize results in the main thread before making edits.

---

## 3. Self-Improvement Loop

* After each user correction, update **tasks/lessons.md** with:
  * what went wrong,
  * the trigger pattern,
  * a prevention rule.
* Before starting significant work, quickly review relevant lessons for this project.
* Prefer concrete, testable rules over vague reminders.

---

## 4. Verification Before Completion

* Do not mark work complete until behavior is validated.
* Run the most relevant checks (tests/lint/typecheck/runtime/logs) for the changed surface area.
* When relevant, compare before/after behavior and confirm no regression.
* If verification cannot be run, explicitly state what was not verified and why.

---

## 5. Elegance Without Over-Engineering

* For non-trivial changes, pause and ask: “What is the simplest durable design?”
* If the fix is brittle, refactor toward the cleaner solution while scope is still small.
* For trivial fixes, prioritize speed and clarity over abstraction.
* Favor minimal, high-leverage edits.

---

## 6. Autonomous Bug Fixing

* On bug reports, move directly to reproduce → isolate root cause → fix → verify.
* Use logs, failing tests, and error traces as primary evidence.
* Minimize user back-and-forth; make reasonable assumptions and state them after execution.
* For CI failures, identify failing jobs/tests and drive to green with verified fixes.

---

## Task Management Workflow

1. Write a checklist plan in **tasks/todo.md**.
2. Confirm assumptions/risks briefly before implementation (only escalate if consequences are non-obvious).
3. Mark checklist items complete as they finish.
4. Record a short “what changed and why” note per major step.
5. Add a final review section in **tasks/todo.md** with verification evidence.
6. If corrected during work, update **tasks/lessons.md**.

---

## Core Principles

* Simplicity first: smallest safe change that fully solves the problem.
* Root-cause over patching: avoid temporary fixes unless explicitly requested.
* Keep momentum: execute end-to-end (implement + verify + summarize).
* Be explicit about uncertainty, assumptions, and residual risk.
